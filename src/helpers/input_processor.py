import os
from pydoc import cli
import polars as pl
import numpy as np
import helpers.audio_tools as adt
from .lut import clinical_iterables, clinical_data
import copy 
import tqdm

<<<<<<< HEAD
def ingestData(data_dir, nan, encode_features=False):
    #feature_list stores all features and feature values as key-value pairs: key = (feature, str), value = (feature value, list)
    feature_list = {
        'patient_id':           [],
        'num_locations':        [],
        'sampling_frequency':   [],
        'audio_files':          [],
        'recording_locations':  [],
        #begin named features
        'age':                  [],
        'sex':                  [],
        'height':               [],
        'weight':               [],
        'pregnancy_status':     [],
        'murmur':               [],
        'murmur_locations':     [],
        'most_audible_location':[],
        'sys_mur_timing':       [],
        'sys_mur_shape':        [],
        'sys_mur_pitch':        [],
        'sys_mur_grading':      [],
        'sys_mur_quality':      [],
        'dia_mur_timing':       [],
        'dia_mur_shape':        [],
        'dia_mur_pitch':        [],
        'dia_mur_grading':      [],
        'dia_mur_quality':      [],
        'outcome':              [],
        'campaign':             [],
        'additional_id':        []
    }

    #features listed in feature_names are all listed in the patient txt file using the form "#" + name + ": " + value. Not all features obey this form, so this object does not store all features
    #stores features and their identifying information as key-value pairs: key = (feature, str), value = (expected text representation of feature in .txt file, str)
    feature_names = {
        'age':                  '#Age',
        'sex':                  '#Sex',
        'height':               '#Height',
        'weight':               '#Weight',
        'pregnancy_status':     '#Pregnancy status',
        'murmur':               '#Murmur',
        'murmur_locations':     '#Murmur locations',
        'most_audible_location':'#Most audible location',
        'sys_mur_timing':       '#Systolic murmur timing',
        'sys_mur_shape':        '#Systolic murmur shape',
        'sys_mur_pitch':        '#Systolic murmur pitch',
        'sys_mur_grading':      '#Systolic murmur grading',
        'sys_mur_quality':      '#Systolic murmur quality',
        'dia_mur_timing':       '#Diastolic murmur timing',
        'dia_mur_shape':        '#Diastolic murmur shape',
        'dia_mur_pitch':        '#Diastolic murmur pitch',
        'dia_mur_grading':      '#Diastolic murmur grading',
        'dia_mur_quality':      '#Diastolic murmur quality',
        'outcome':              '#Outcome',
        'campaign':             '#Campaign',
        'additional_id':        '#Additional ID'
    }

    #load cipher for encoding features as numbers
    encode, decode = load_cipher(nan)
=======
>>>>>>> 4fb3c656919e3a5692a84eac754a5b3523fac081

def ingest_data(data_dir):
    print("Ingesting data from ", data_dir  )
    # we use the deepcopy function to avoid overwriting the original clinical_iterables
    # otherwise this creates a super hard to find bug where running the code multiple times
    # will result in the output being different each time
    data = copy.deepcopy(clinical_data)
    for file in os.listdir(data_dir):
        if file.endswith(".txt"):
            # open text file
            with open(data_dir + "/" + file, "r") as f:
<<<<<<< HEAD

                #create temporary containers to store features with multiple values
                patient_audio_files = []
                patient_recording_locations = []

                #iterate through each line in file
                for line_number, line in enumerate(f):

                    #get info from first line: first number is patient_id, second number is num_locations, third number is sampling_frequency
                    if line_number==0:
                        first_line = line.split(" ")
                        patient_id, num_locations, sampling_frequency = int(first_line[0]), int(first_line[1]), int(first_line[2])
                        feature_list['patient_id'].append(patient_id)
                        feature_list['num_locations'].append(num_locations)
                        feature_list['sampling_frequency'].append(sampling_frequency)

                    #get audio file names
                    elif line_number in range(1, num_locations+1):
                        moving_line = line.strip().split(" ")
                        current_recording_location, current_audio_file = moving_line[0], moving_line[2]

                        #encode features
                        if encode_features==True:
                            current_recording_location = encode['recording_locations'][current_recording_location]

                        patient_audio_files.append(current_audio_file)
                        patient_recording_locations.append(current_recording_location)

                    #get named features
                    elif line_number>num_locations:
                        #determine which feature is defined in this line and read data accordingly
                        for current_named_feature in feature_names.keys():
                            if line.startswith(feature_names[current_named_feature] + ":"):
                                val = line.split(': ', 1)[1].strip()
                                if current_named_feature=='murmur_locations':
                                    val = val.split('+')

                                #encode features
                                if encode_features==True:
                                    if current_named_feature in ['height', 'weight']: #convert to int
                                        if val=='nan':
                                            val = nan
                                        else:
                                            val = int(float(val))
                                    elif current_named_feature=='murmur_locations': #encode strings in list as numbers
                                        for i, entry in enumerate(val):
                                            val[i] = encode[current_named_feature][entry]
                                    elif not current_named_feature in ['campaign', 'additional_id']: #encode string as number
                                        val = encode[current_named_feature][val]

                                feature_list[current_named_feature].append(val)


                #push to feature_list all features that have not yet been stored there
                feature_list['audio_files'].append(patient_audio_files)
                feature_list['recording_locations'].append(patient_recording_locations)

    print('finished reading from files')

    #Create a dataframe to store the data
    df = pl.DataFrame(feature_list)
    
    return df

#TODO: when exploding audio,files, only some locations have murmurs, address this

#PURPOSE:   load training data for input into ML model
#PARAMS:    data_dir            str         path to directory containing training data files
#           features            list(str)   list of features to pass to ML model
#           nan                 any         value to encode 'nan' entries as
#           encode_features     Bool        [OPTIONAL] whether to encode features as numbers: default=False
#RETURNS:   pl.DataFrame    dataframe storing spectrograms and features
def load_training_data(features, data_dir, nan, encode_features=False):

    #load data into dataframe
    df = ingestData(data_dir, nan, encode_features=encode_features)
=======
                # read first line
                line = f.readline()
                # split line into list
                line = line.strip().split(" ")
                data['patient_id'].append(line[0])
                data['num_locations'].append(line[1])
                data['sampling_frequency'].append(line[2])
                # loop through each line to check if it maches with an iterables
                audio_files = []
                recording_locations = []
                for line in f:
                    # check if line contains .wav
                    if ".wav" in line:
                        # split the line 
                        line_split = line.split(" ")
                        audio_files.append(line_split[2]) 
                        recording_locations.append(line_split[0]) 
                    for iterable in clinical_iterables:
                        if line.startswith(clinical_iterables[iterable] + ":"):
                            # get the value of the iterable
                            value = line.split(': ', 1)[1].strip()
                            # add the value to the data
                            data[iterable].append(value)
                data['audio_files'].append(audio_files)
                data['recording_locations'].append(recording_locations)
    df = pl.DataFrame(data)
    return df

def files_to_spectro(fileArray, path="", sr=4000):
    print("Generating spectrograms...")
    length = 0
    spectros = []

    #get length of nested array
    for array in fileArray:
        length += len(array)
>>>>>>> 4fb3c656919e3a5692a84eac754a5b3523fac081

    progress = tqdm.tqdm(total=length, desc="Generating spectrograms")
    for array in fileArray:
        patientSpectros = []
        for file in array:
            spectro = adt.wav_to_spectro(path + "/" + file, sr=sr)
            patientSpectros.append(spectro)
            progress.update(1)
        spectros.append(patientSpectros)
    progress.close()

    return spectros

            


    

    