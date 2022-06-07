import os
from pydoc import cli
import polars as pl
import numpy as np
import helpers.audio_tools as adt
from .lut import clinical_iterables, clinical_data, data_cipher
import copy 
import tqdm

#returns dataframe storing comprehensive data (including spectrograms) for each audio file
#data_dir       str     path to directory storing training data (.txt and .wav files for each subject, etc)
#cache_dir      str     path to directory storing copy of ingested data (or, if it does not yet exist, where a copy will be stored)
#encode_data    Bool    [OPTIONAL] whether the data should be encoded
def ingest_data(data_dir, cache_dir, encode_data=False):

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
        print("Ingesting data from ", data_dir)
        # we use the deepcopy function to avoid overwriting the original clinical_iterables
        # otherwise this creates a super hard to find bug where running the code multiple times
        # will result in the output being different each time
        data = copy.deepcopy(clinical_data)

        #loop through txt files in directory
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
                    
                    # loop through each line to check if it maches with an iterables or if it contains a wav file
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

                    #add each audio file and corresponding recording location to data as its own line
                    #for all lines added, extend remaining columns and fill with the data collected for this file
                    num_locations = data['num_locations'][-1]
                    for column in data:
                        if column=='audio_files':
                            data[column].extend(audio_files)
                        elif column=='recording_locations':
                            data[column].extend(recording_locations)
                        else:
                            extend_by = num_locations - 1
                            fill_with_value = data[column][-1]
                            data[column].extend([fill_with_value for x in range(extend_by)])

        #get spectrogram for each wav file
        data['spectrogram'] = files_to_spectro(data['audio_files'], path=data_dir, output_folder=cache_dir+'/spectrograms')
        #store data as a dataframe
        df = pl.DataFrame(data)
        df.write_json(cache_dir + '/' + cache)

    if encode_data:
        encoded_data = encodeData(df.to_dict())
        df = pl.DataFrame(encoded_data)

    return df

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

    progress = tqdm.tqdm(total=length, desc="Generating spectrograms")
    for array in workingFileArray:
        patientSpectros = []
        for file in array:
            spectro = adt.wav_to_spectro(path + "/" + file, sr=sr)
            spectro_file = output_folder + '/' + file.replace('.wav', '.npy')
            np.save(spectro_file, spectro)

            patientSpectros.append(spectro_file)
            progress.update(1)
        spectros.append(patientSpectros)
    progress.close()

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
    working_data = data.copy()
    cipher = data_cipher.copy()

    #cast numeric data to float type
    for column in ['patient_id', 'num_locations', 'sampling_frequency', 'height', 'weight', 'additional_id']:
        working_data[column] = [float(x) for x in working_data[column]]

    #for each entry in data['murmur_locations']: split into list, then encode each element of list using cipher
    mod_entry = lambda entry: [cipher['murmur_locations'][y] for y in entry.strip().split('+')]
    working_data['murmur_locations'] = [mod_entry(x) for x in working_data['murmur_locations']]

    #encode remaining data
    for column in cipher:
        if not column=='murmur_locations':
            working_data[column] = [cipher[column][x] for x in working_data[column]]

    return working_data