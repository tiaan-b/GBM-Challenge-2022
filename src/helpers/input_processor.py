import os
from pydoc import cli
import polars as pl
import numpy as np
import helpers.audio_tools as adt
from .lut import clinical_iterables, clinical_data
import copy 
import tqdm


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

            


    

    