import os
from pydoc import cli
import polars as pl
import numpy as np
import helpers.audio_tools as adt
import helpers.lut as lut
import tqdm

def ingest_data(data_dir, rebuild=False):

    spectro_cache = adt.dir_to_spectro(data_dir, rebuild=rebuild)

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


