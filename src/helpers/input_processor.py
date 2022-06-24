import os
from pydoc import cli
import polars as pl
import numpy as np
import helpers.audio_tools as adt
import helpers.lut as lut
import tqdm

def __getCacheDir():
    return 'cache'

def loadTrainingData(data_dir, encode_data=False):
    #file to store ingested data, inside cache_dir directory
    cache_dir = __getCacheDir()
    cache_file = 'ingested_data.json'
    
    #check if data has already been ingested and stored in cache_file
    os.makedirs(cache_dir, exist_ok=True)
    desired_audio_files = [x for x in os.listdir(data_dir) if x.endswith('.wav')]
    data_is_saved = __checkCachedDataframe(desired_audio_files, cache_dir, cache_file)
    
    #load df from save file if it exists, otherwise generate df from raw data
    if data_is_saved:
        print('loading data from save file: ', cache_dir + '/' + cache_file)
        df = pl.read_json(cache_dir + '/' + cache_file)
    else:
        print("loading raw data from ", data_dir)
        nested_data = ['audio_file', 'recording_location']
        df = (
            __ingest_data(data_dir)
            .explode(nested_data)           #explode df so that each audio file and its corresponding recording location is on its own line
            .pipe(__getMurmurInRecording)   #get murmur_in_recording (whether a murmur is present in the corresponding recording)
            .pipe(reorderCols)
        )
        #save df to file. Future calls to loadData will load the df from this file
        df.write_json(cache_dir + '/' + cache_file)

    if encode_data:
        df = encodeData(df)

    return df


def getSpectrogram(df, data_dir):

    #check if df already has a spectrogram column
    if 'spectrogram' in df.columns:
        return df

    spectro_dir = __getCacheDir() + '/spectrograms'
    os.makedirs(spectro_dir, exist_ok=True)

    #check if spectrograms have already been created and stored in cache
    desired_spectros = df.get_column('audio_file').apply(lambda x: x.replace('.wav', '.npy')).to_list()
    spectros_are_saved = __checkCachedSpectros(desired_spectros, spectro_dir)

    if spectros_are_saved:
        length = df.height
        progress = tqdm.tqdm(total=length, desc="Loading spectrograms from cache")
        out = df.with_column(
            pl.col('audio_file').str.replace('.wav', '.npy')
            .apply(lambda x: __function_with_logUpdater(progress, np.load(spectro_dir + '/' + x)))
            .alias('spectrogram')
        )
        progress.close()
    else:
        length = df.height * 2
        progress = tqdm.tqdm(total=length, desc="Generating spectrograms")
        out = df.with_column(
            pl.col('audio_file')
            .apply(lambda x: __function_with_logUpdater(progress, __file_to_spectro(x, path=data_dir, output_folder=spectro_dir)))
            .apply(lambda x: __function_with_logUpdater(progress, np.load(spectro_dir + '/' + x)))
            .alias('spectrogram')
        )
        progress.close()
    
    out = reorderCols(out)
    return out


def encodeData(data):
    #assume no duplicate column names

    #check if data is a polars dataframe
    if not isinstance(data, pl.internals.frame.DataFrame):
        raise Exception('data is of unsupported type "{}". Supported types include polars.internals.frame.DataFrame'.format(data.type()))

    cipher = lut.getCipher()
    data_columns = data.columns
    numeric_data = [x for x in ['patient_id', 'total_locations', 'sampling_frequency', 'height', 'weight', 'additional_id'] if x in data_columns]
    cipher_friendly_data = [x for x in cipher.keys() if x in data_columns and x!='murmur_locations']
    unencoded_data = [x for x in data_columns if x not in (*numeric_data, *cipher_friendly_data, 'murmur_locations')]

    out = data.select([
        #cast numeric data to float type
        pl.col(numeric_data)
        .cast(pl.datatypes.Float64),

        #in murmur_locations: encode each element of each list in column using cipher
        pl.col('murmur_locations').arr.eval(pl.element().apply(lambda x: cipher['murmur_locations'][x])),

        #encode cipher friendly data
        pl.col(cipher_friendly_data)
        .map(lambda x: __applyCipher(x, cipher)),

        pl.col(unencoded_data)
    ])

    out = reorderCols(out)

    return out


def reorderCols(data):
    #assume no duplicate column names in data
    all_cols = data.columns

    #desired order of columns
    ordered_cols = [
        'patient_id',           
        'murmur_in_patient',               
        'audio_file', 
        'spectrogram',
        'mfcc',
        'murmur_in_recording',         
        'recording_location',  
        'sampling_frequency',   
        'total_locations',        
        'murmur_locations',     
        'most_audible_location',
        'outcome',              
        'age',                  
        'sex',                  
        'height',               
        'weight',               
        'pregnancy_status',     
        'sys_mur_timing',       
        'sys_mur_shape',        
        'sys_mur_pitch',        
        'sys_mur_grading',      
        'sys_mur_quality',      
        'dia_mur_timing',       
        'dia_mur_shape',        
        'dia_mur_pitch',        
        'dia_mur_grading',      
        'dia_mur_quality',      
        'campaign',             
        'additional_id',        
    ]
    ordered_cols = [x for x in ordered_cols if x in all_cols]

    #remaining columns with no specified order
    unordered_cols = sorted(set(all_cols).difference(set(ordered_cols)))

    #columns are ordered as specified in order_cols.
    #remaining columns are included afterwards.
    out = data.select([*ordered_cols, *unordered_cols])
    
    return out

########################################################################
#   PRIVATE FUNCTIONS
########################################################################

def __ingest_data(data_dir):

    data = lut.getClinicalData()
    clinical_iterables = lut.getClinicalIterables()

    #loop through txt files in directory
    total_txt_files = len([x for x in os.listdir(data_dir) if x.endswith('.txt')])
    progress = tqdm.tqdm(total=total_txt_files, desc="Reading from .txt files in "+data_dir)
    for file in os.listdir(data_dir):
        if file.endswith(".txt"):
            # open text file
            with open(data_dir + "/" + file, "r") as f:

                # read first line
                line = f.readline()
                # split line into list
                line = line.strip().split(" ")
                data['patient_id'].append(int(line[0]))
                data['total_locations'].append(int(line[1]))
                data['sampling_frequency'].append(int(line[2]))
                
                # loop through each line to check if it matches with an iterables or if it contains a wav file
                audio_files = []
                recording_locations = []
                for line in f:
                    # check if line contains .wav
                    if ".wav" in line:
                        # split the line 
                        line_split = line.split(" ")
                        audio_files.append(line_split[2]) 
                        recording_locations.append(line_split[0]) 
                    #loop through iterables to check if line matches with any of them
                    else:
                        for iterable in clinical_iterables:
                            if line.startswith(clinical_iterables[iterable] + ":"):
                                # get the value of the iterable
                                value = line.split(': ', 1)[1].strip()
                                # add the value to the data
                                data[iterable].append(value)
                                break

                data['audio_file'].append(audio_files)
                data['recording_location'].append(recording_locations)
                progress.update(1)
    progress.close()

    #save data in polars Dataframe
    df = pl.DataFrame(data)

    #split each element in murmur_locations (type=str) into list
    df = df.with_column(pl.col('murmur_locations').str.split(by='+'))

    return df


def __getMurmurInRecording(data):
    out = data.with_column(
        pl.when(pl.col('murmur_in_patient')==('Absent' or 'Unknown'))
        .then(pl.col('murmur_in_patient'))
        .when(pl.all([
            pl.col('murmur_in_patient')=='Present',
            pl.col('recording_location').is_in('murmur_locations')
        ]))
        .then('Present')
        .otherwise('Absent')
        .alias('murmur_in_recording')
    )

    return out


def __file_to_spectro(file, path="", output_folder='', sr =4000):
    os.makedirs(output_folder, exist_ok=True)
    spectro = adt.wav_to_spectro(path + "/" + file, sr=sr)
    spectro_file = file.replace('.wav', '.npy')
    np.save(output_folder + '/' + spectro_file, spectro)

    return spectro_file


def __function_with_logUpdater(progress, func):
    progress.update(1)
    out = func
    return out

#assumes data_dir and cache_dir both exist
def __checkCachedDataframe(desired_audio_files, cache_dir, save_file):            
    #check if save file exists in cache_dir
    if save_file not in os.listdir(cache_dir):
        data_is_saved = False
    else:
        try:
            #check if saved data matches the desired data
            saved_data = pl.read_json(cache_dir + '/' + save_file)
            saved_audio_files = saved_data.get_column('audio_file').to_list()
            if set(saved_audio_files) == set(desired_audio_files):
                data_is_saved = True
            else:
                data_is_saved = False
        except Exception as e:
            print(
                'An unexpected error occured while trying to check the cache file \n' +
                '\'%s\' in the cache directory \'%s\'\n' % (save_file, cache_dir) +
                ' (see below for error message). \n\n' +
                'Troubleshooting:\n' + 
                ' - make sure that the cache directory exists\n' + 
                ' - try deleting cache file and running program again\n'
            )
            raise
    return data_is_saved

#assumes cache_dir exists
def __checkCachedSpectros(desired_spectros, spectro_dir):
    saved_spectros = os.listdir(spectro_dir)
    if set(desired_spectros).issubset(set(saved_spectros)):
        spectros_are_saved = True
    else:
        spectros_are_saved = False
    return spectros_are_saved

    

def __applyCipher(col, cipher):
    col_name = col.name
    out = col.apply(lambda x: cipher[col_name][x])
    return out