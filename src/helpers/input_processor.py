import os
from pydoc import cli
import polars as pl
import numpy as np
import helpers.audio_tools as adt
from .lut import clinical_iterables, clinical_data, data_cipher
import copy 
import tqdm

def loadData(data_dir, cache_dir, encode_data=False):
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
        
        df = ingest_data(data_dir)
        #get spectrogram for each wav file
        length = df.height
        progress = tqdm.tqdm(total=length, desc="Generating spectrograms")
        df = df.with_column(
            pl.col('audio_files')
            .apply(lambda x: __function_with_logUpdater(progress, files_to_spectro(x, path=data_dir, output_folder=cache_dir+'/spectrograms')))
            .alias('spectrogram')
        )
        progress.close()
        #explode data so that each audio file and its corresponding recording location, spectrogram is on its own line in data
        nested_data = ['audio_files', 'recording_locations', 'spectrogram']
        df = df.explode(nested_data)
        #save df to file. Future calls to loadData will load the df from this file
        df.write_json(cache_dir + '/' + cache)

    if encode_data:
        df = encodeData(df)

    return df


def ingest_data(data_dir):

    # we use the deepcopy function to avoid overwriting the original clinical_iterables
    # otherwise this creates a super hard to find bug where running the code multiple times
    # will result in the output being different each time
    data = copy.deepcopy(clinical_data)

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
                data['num_locations'].append(int(line[1]))
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

                data['audio_files'].append(audio_files)
                data['recording_locations'].append(recording_locations)
                progress.update(1)
    progress.close()

    df = pl.DataFrame(data)

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
    nested_data = ['audio_files', 'recording_locations', 'spectrogram']
    
    #iterate through each row in data
    length = len(input_data['patient_id'])
    progress = tqdm.tqdm(total=length, desc="Reshaping data")
    for i in range(len(input_data['patient_id'])):
        num_locations = input_data['num_locations'][i]
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
        saved_audio_files = saved_data.get_column('audio_files').to_list()
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

    cipher = data_cipher.copy()
    data_columns = data.columns
    numeric_data = [x for x in data_columns if x in ['patient_id', 'num_locations', 'sampling_frequency', 'height', 'weight', 'additional_id']]
    unencoded_data = [x for x in data_columns if x in ['audio_files', 'spectrogram']]
    cipher_friendly_data = [x for x in data_columns if x in cipher.keys() and x!='murmur_locations']

    out = data.select([
        #include unencoded data
        pl.col(unencoded_data),

        #cast numeric data to float type
        pl.col(numeric_data)
        .cast(pl.datatypes.Float64),

        #for each element in murmur_locations: split into list, then encode each element of list using cipher
        pl.col('murmur_locations').str.split(by='+')
        .arr.eval(pl.element().apply(lambda x: cipher['murmur_locations'][x])),

        #encode remaining data using cipher
        pl.col(cipher_friendly_data)
        .map(lambda x: __applyCipher(x, cipher))
    ])

    return out

def __applyCipher(col, cipher):
    col_name = col.name
    out = col.apply(lambda x: cipher[col_name][x])
    return out