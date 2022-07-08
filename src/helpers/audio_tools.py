import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os
import tqdm

#####################################################################
#  PURPOSE:   PRODUCES THE SPECTROGRAM OF THE SPECIFIED .WAV FILE   #
#       PARAMS:    WAV_FILE    STR     PATH TO THE .WAV FILE        #
# RETURNS:   NDARRAY OF FLOAT32 - SPECTROGRAM OF INPUTTED .WAV FILE #
#####################################################################

def wav_to_spectro(wav_file, sr=4000):
    waveform, samp_rate = librosa.load(wav_file, sr=sr) #make sure that the correct sample rate is passed as a parameters. if unspecified, the function chooses some default value
    x = librosa.stft(waveform)
    xDb = librosa.amplitude_to_db(np.abs(x))
    spectro = __normalize_spectro(xDb)
    return spectro

def __normalize_spectro(spectro):
    return (spectro - np.min(spectro)) / (np.max(spectro) - np.min(spectro))

def dir_to_spectro(dir_path, cache_path="data/__spectro_cache__", sr=4000, rebuild=False):
    # for files in dir_path if ends with .wav
    # convert to spectrogram
    # save into cache
    if not os.path.exists(cache_path):
        print("Creating cache directory")
        os.makedirs(cache_path)
    elif not rebuild:
        print("Cache already exists. Skipping cache creation")
        return cache_path

    
    # count all wav files in dir_path
    wav_files = [f for f in os.listdir(dir_path) if f.endswith(".wav")]
    num_files = len(wav_files)

    # create progress bar
    pbar = tqdm.tqdm(total=num_files)
    pbar.set_description("Converting wavs to spectrograms")

    spectros = []

    for wav_file in tqdm.tqdm(wav_files):
        wav_path = os.path.join(dir_path, wav_file)
        spectro = wav_to_spectro(wav_path, sr=sr)
        spectro_path = os.path.join(cache_path, wav_file.replace(".wav", ".npy"))
        np.save(spectro_path, spectro)
        pbar.update(1)
    return cache_path





