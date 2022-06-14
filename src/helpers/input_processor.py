import os
from pydoc import cli
import polars as pl
import numpy as np
import helpers.audio_tools as adt
import helpers.lut as lut
import tqdm

def loadTrainingData(data_dir, cache_dir, encode_data=False):
    #file to store ingested data, inside cache_dir directory
    cache = 'ingested_data.json'
    
    #check if data has already been ingested and stored in cache
    os.makedirs(cache_dir, exist_ok=True)
    data_is_saved = __checkCache(data_dir, cache_dir, cache)
    
    #load df from save file if it exists, otherwise generate df from raw data
    if data_is_saved:
        print('loading data from save file: ', cache_dir + '/' + cache)
        df = pl.read_json(cache_dir + '/' + cache)
    else:
        print("loading raw data from ", data_dir)
        nested_data = ['audio_file', 'recording_location']
        df = (
            ingest_data(data_dir)
            .explode(nested_data)                       #explode df so that each audio file and its corresponding recording location is on its own line
            .pipe(getSpectrogram, data_dir, cache_dir)  #get spectrogram for each wav file
            .pipe(getMurmurInRecording)                 #get murmur_in_recording (whether a murmur is present in the corresponding recording)
            .pipe(reorderCols)
        )
        #save df to file. Future calls to loadData will load the df from this file
        df.write_json(cache_dir + '/' + cache)

    if encode_data:
        df = encodeData(df)

    return df


def ingest_data(data_dir):

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
    df.replace(
        'murmur_locations',
        df.get_column('murmur_locations').str.split(by='+')
    )

    return df


def reshapeData(data):
    #preprocessing
    if isinstance(data, dict):
        data_type = 'dict'
        input_data = data.copy()
    elif isinstance(data, pl.internals.frame.DataFrame):
        data_type = 'DataFrame'
        input_data = data.to_dict()
    else:
        raise Exception('data is of unsupported type "{}". Supported types include polars.internals.frame.DataFrame and dict'.format(data.type()))
    sorted_data = {k:[] for k in input_data.keys()}
    nested_data = ['audio_file', 'recording_location', 'spectrogram']
    
    #iterate through each row in data
    length = len(input_data['patient_id'])
    progress = tqdm.tqdm(total=length, desc="Reshaping data")
    for i in range(len(input_data['patient_id'])):
        num_locations = input_data['total_locations'][i]
        for column in input_data.keys():
            if column in nested_data:
                sorted_data[column].extend(input_data[column][i])
            else:
                fill_value = input_data[column][i]
                sorted_data[column].extend([fill_value for x in range(num_locations)])
        progress.update(1)
    progress.close()

    #decide what type of object to return
    if data_type=='DataFrame':
        out = pl.DataFrame(sorted_data)
    else:
        out = sorted_data

    return out


def __function_with_logUpdater(progress, func):
    progress.update(1)
    out = func
    return out


def file_to_spectro(file, path="", output_folder='', sr =4000):
    spectro = adt.wav_to_spectro(path + "/" + file, sr=sr)
    spectro_file = output_folder + '/' + file.replace('.wav', '.npy')
    np.save(spectro_file, spectro)

    return spectro_file


def files_to_spectro(fileArray, path="", output_folder="", sr=4000):
    length = 0
    spectros = []
    workingFileArray = []

    os.makedirs(output_folder, exist_ok=True)

    #check whether fileArray is nested
    if any(isinstance(x, list) for x in fileArray):
        isNested = True
        workingFileArray = fileArray
    else:
        isNested = False
        #'cast' fileArray to nested array of length 1
        workingFileArray.append(fileArray)

    #get length of nested array
    for array in workingFileArray:
        length += len(array)

    #progress = tqdm.tqdm(total=length, desc="Generating spectrograms")
    for array in workingFileArray:
        patientSpectros = []
        for file in array:
            spectro = adt.wav_to_spectro(path + "/" + file, sr=sr)
            spectro_file = output_folder + '/' + file.replace('.wav', '.npy')
            np.save(spectro_file, spectro)

            patientSpectros.append(spectro_file)
            #progress.update(1)
        spectros.append(patientSpectros)
    #progress.close()

    #return an un-nested list if the array passed as fileArray was also un-nested
    if not isNested:
        spectros = spectros[0]

    return spectros


def __checkCache(data_dir, cache_dir, cache):
    data_is_saved = False
    #check if save file exists
    if cache in os.listdir(cache_dir):
        saved_data = pl.read_json(cache_dir + '/' + cache)
        #check if saved data matches the desired data
        saved_audio_files = saved_data.get_column('audio_file').to_list()
        saved_spectros = os.listdir(cache_dir + '/spectrograms')
        desired_audio_files = [x for x in os.listdir(data_dir) if x.endswith('.wav')]
        desired_spectros = [x.replace('.wav', '.npy') for x in desired_audio_files]
        if set(saved_audio_files) == set(desired_audio_files) and set(desired_spectros).issubset(set(saved_spectros)):
            data_is_saved = True
    return data_is_saved


def encodeData(data):
    #check if data is a polars dataframe
    if not isinstance(data, pl.internals.frame.DataFrame):
        raise Exception('data is of unsupported type "{}". Supported types include polars.internals.frame.DataFrame'.format(data.type()))

    cipher = lut.getCipher()
    data_columns = data.columns
    numeric_data = [x for x in data_columns if x in ['patient_id', 'total_locations', 'sampling_frequency', 'height', 'weight', 'additional_id']]
    unencoded_data = [x for x in data_columns if x in ['audio_file', 'spectrogram']]
    cipher_friendly_data = [x for x in data_columns if x in cipher.keys() and x!='murmur_locations']

    out = data.select([
        #cast numeric data to float type
        pl.col(numeric_data)
        .cast(pl.datatypes.Float64),

        #in murmur_locations: encode each element of each list in column using cipher
        pl.col('murmur_locations').arr.eval(pl.element().apply(lambda x: cipher['murmur_locations'][x])),

        #encode remaining data using cipher
        pl.col(cipher_friendly_data)
        .map(lambda x: __applyCipher(x, cipher)),

        #include unencoded data
        pl.col(unencoded_data)
    ])

    return out

def __applyCipher(col, cipher):
    col_name = col.name
    out = col.apply(lambda x: cipher[col_name][x])
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


def getMurmurInRecording(data):
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


def getSpectrogram(data, data_dir, cache_dir):
    length = data.height
    progress = tqdm.tqdm(total=length, desc="Generating spectrograms")
    out = data.with_column(
        pl.col('audio_file')
        .apply(lambda x: __function_with_logUpdater(progress, file_to_spectro(x, path=data_dir, output_folder=cache_dir+'/spectrograms')))
        .alias('spectrogram')
    )
    progress.close()
    
    return out