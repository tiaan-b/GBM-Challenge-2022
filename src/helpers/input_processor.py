import os
import polars as pl
import numpy

def ingestData(data_dir):
    #(template) stores all features and feature values as key-value pairs: key = (feature, str), value = (feature value, list)
    feature_list = {
        'patient_id': [],
        'num_locations': [],
        'sampling_frequency': [],
        #'audio_files': [],
        'recording_locations': [],
        #begin named features
        'age': [],
        'sex': [],
        'height': [],
        'weight': [],
        'pregnancy_status': [],
        'murmur': [],
        'murmur_locations': [],
        'most_audible_location': [],
        'sys_mur_timing': [],
        'sys_mur_shape': [],
        'sys_mur_grading': [],
        'sys_mur_pitch': [],
        'sys_mur_quality': [],
        'dia_mur_timing': [],
        'dia_mur_shape': [],
        'dia_mur_grading': [],
        'dia_mur_pitch': [],
        'dia_mur_quality': [],
        'outcome': [],
        'campaign': [],
        'additional_id': []
    }

    #features listed in feature_names are all listed in the patient txt file using the form "#" + name + ": " + value. Not all features obey this form, so this object does not store all features
    #stores features and their identifying information as key-value pairs: key = (feature, str), value = (expected text representation of feature in .txt file, str)
    feature_names = {
        'age': '#Age',
        'sex': '#Sex',
        'height': '#Height',
        'weight': '#Weight',
        'pregnancy_status': '#Pregnancy status',
        'murmur': '#Murmur',
        'murmur_locations': '#Murmur locations',
        'most_audible_location': '#Most audible location',
        'sys_mur_timing': '#Systolic murmur timing',
        'sys_mur_shape': '#Systolic murmur shape',
        'sys_mur_grading': '#Systolic murmur grading',
        'sys_mur_pitch': '#Systolic murmur pitch',
        'sys_mur_quality': '#Systolic murmur quality',
        'dia_mur_timing': '#Diastolic murmur timing',
        'dia_mur_shape': '#Diastolic murmur shape',
        'dia_mur_grading': '#Diastolic murmur grading',
        'dia_mur_pitch': '#Diastolic murmur pitch',
        'dia_mur_quality': '#Diastolic murmur quality',
        'outcome': '#Outcome',
        'campaign': '#Campaign',
        'additional_id': '#Additional ID'
    }

    #create polars DataFrame to store the data
    master_features = pl.DataFrame()

    print("Ingesting data from ", data_dir  )
    
    # Loop through all text files in the data directory
    for file in os.listdir(data_dir):
        if file.endswith(".txt"):
            # Open text file
            with open(data_dir + "/" + file, "r") as f:

                print("opened " + file)

                patient_features = feature_list
                
                #create temporary containers to store features with multiple values
                patient_audio_files = []
                patient_recording_locations = []

                #iterate through each line in file
                for line_number, line in enumerate(f):

                    #get info from first line: first number is patient_id, second number is num_locations, third number is sampling_frequency
                    if line_number==0:
                        first_line = line.split(" ")
                        patient_id, num_locations, sampling_frequency = int(first_line[0]), int(first_line[1]), int(first_line[2])
                        patient_features['patient_id'].append(patient_id)
                        patient_features['num_locations'].append(num_locations)
                        patient_features['sampling_frequency'].append(sampling_frequency)
                        print('complete: read from first line')

                    #get audio file names and locations, store as list of tuples. also store locations in list of all recording locations
                    elif line_number in range(1, num_locations+1):
                        moving_line = line.strip().split(" ")
                        current_recording_location, current_audio_file = moving_line[0], moving_line[2]
                        patient_audio_files.append((current_audio_file, current_recording_location))
                        patient_recording_locations.append(current_recording_location)
                        print('complete: recorded an audio file name')

                    #get named features
                    elif line_number>num_locations:
                        for current_named_feature in feature_names.keys():
                            if line.startswith(feature_names[current_named_feature] + ":"):
                                patient_features[current_named_feature].append(line.split(': ', 1)[1].strip())
                                print('complete: recorded a named feature')

                #push to patient_features all features that have not yet been stored there
                #patient_features['audio_files'].append(patient_audio_files)
                patient_features['recording_locations'].append(patient_recording_locations)

                print('finished reading from ' + file)
                print(patient_features)

                #return patient_features

                #add patient_features to master_features
                df = pl.DataFrame(patient_features)
                print('created a dataframe from patient data')

                if master_features.is_empty():
                    master_features = pl.DataFrame(patient_features)
                else:
                    master_features.vstack(pl.DataFrame(patient_features), True)

                # master_features.with_columns(
                #     [
                #         #pl.when(master_features.is_empty()).then(master_features.replace(master_features.columns, pl.DataFrame(patient_features).get_columns())).otherwise(master_features.vstack(pl.DataFrame(patient_features)))
                #         pl.when(master_features.is_empty())
                #         .then(
                #             master_features.drop(name)
                #         )
                #         .otherwise(master_features.vstack(pl.DataFrame(patient_features)))

                #     ]
                # )


                # master_features.vstack(pl.DataFrame(patient_features))
                print('added patient features to master features')

    #Create a polars object to store the data
    #df = pl.DataFrame(feature_list)
    print('finished reading from all files')
    return df

#PURPOSE:   produces the spectrogram of the specified .wav file
#PARAMS:    wav_file    str     path to the .wav file
#RETURNS:   ndarray of float32 - spectrogram of inputted .wav file
def wav_to_spectro(wav_file):
    sample_rate, samples = wavfile.read(wav_file)
    frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)
    return spectrogram

#PURPOSE:   loads an invertable dictionary that allows for encoding/decoding patient features as numbers
#RETURNS:   tuple - a tuple containing the following elements:
#               dict - a dict object used to encode features. Each key stores the name of a feature as a string, and the corresponding value is a dict object (where each key is a possible feature_value stored as a str, and the corresponding value is a number used to encode for the feature_value)
#               dict - a dict object used to decode features. Each key stores the name of a feature as a string, and the corresponding value is a dict object (where each key is a number used to encode for a feature_value, and the corresponding value is the feature_value stored as a str)
def load_cipher():
    encode = {
    'Age':                      {'Neonate': 0.5, 'Infant': 6, 'Child': 6*12, 'Adolescent': 15*12, 'Young Adult': 20*12}, #represent each age group as the approximate number of months for the middle of the age group
    'Sex':                      {'Male': 0, 'Female': 1},
    'Pregnancy status':         {'True': 1, 'False': 0},
    'Murmur':                   {'Present': 1, 'Absent': 0, 'Unkown': 2},
    'location':                 {'PV': 0, 'TV': 1, 'AV': 2, 'MV': 3, 'Phc': 4},
    'Systolic murmur timing':   {'Early-systolic': 0, 'Holosystolic': 1, 'Mid-systolic': 2, 'Late-systolic': 3},
    'Systolic murmur shape':    {'Crescendo': 0, 'Decrescendo': 1, 'Diamond': 2, 'Plateau': 3},
    'Systolic murmur pitch':    {'Low': 0, 'Medium': 1, 'High': 2},
    'Systolic murmur grading':  {'I/VI': 0, 'II/VI': 1, 'III/VI': 2},
    'Systolic murmur quality':  {'Blowing': 0, 'Harsh': 1, 'Musical': 2},
    'Diastolic murmur timing':  {'Early-diastolic': 0, 'Holodiastolic': 1, 'Mid-diastolic': 2},
    'Diastolic murmur shape':   {'Crescendo': 0, 'Decrescendo': 1, 'Diamond': 2, 'Plateau': 3}, #note: only decresendo and plateau are actually used, other items are included for consistency with 'systolic murmur shape'
    'Diastolic murmur pitch':   {'Low': 0, 'Medium': 1, 'High': 2},
    'Diastolic murmur grading': {'I/IV': 0, 'II/IV': 1, 'III/IV': 2},
    'Diastolic murmur quality': {'Blowing': 0, 'Harsh': 1, 'Musical': 2}, #note: only blowing and harsh are actually used, other items are included for consistency with 'systolic murmur quality'
    'Outcome':                  {'Abnormal': 0, 'Normal': 1}
    }

    decode = {}
    for feature_name, feature_values in encode.items():
        decode[feature_name] = invert_dict(feature_values)

    return encode, decode


#PURPOSE:   inverts a dict object that obeys one-to-one mapping of key-value pairs; the key and value of any given original key-value pair are the value and key of the new key-value pair, respectively.
#PARAMS:    dict_in     dict    the original dict object that is to be inverted
#RETURNS:   dict - the inverted dict object
def invert_dict(dict_in):
    #check that dict_in obeys one to one mapping
    keys_in = dict_in.keys()
    values_in = dict_in.values()
    if not (len(keys_in)==len(set(keys_in)) and len(values_in)==len(set(values_in))):
        raise Exception('The inputted dict object does not obey one to one mapping of key-value pairs')

    dict_out = {}
    for key, value in dict_in.items():
        dict_out[value] = key
    
    return dict_out