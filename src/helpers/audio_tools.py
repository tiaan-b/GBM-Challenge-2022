from scipy import signal
from scipy.io import wavfile
from pydub import AudioSegment
import librosa
import numpy as np
import matplotlib.pyplot as plt
from librosa import display

#####################################################################
#  PURPOSE:   PRODUCES THE SPECTROGRAM OF THE SPECIFIED .WAV FILE   #
#       PARAMS:    WAV_FILE    STR     PATH TO THE .WAV FILE        #
# RETURNS:   NDARRAY OF FLOAT32 - SPECTROGRAM OF INPUTTED .WAV FILE #
#####################################################################



def wav_to_spectrogram(wav_file):
    waveform, samp_rate = librosa.load(wav_file, sr=4000) #make sure that the correct sample rate is passed as a parameters. if unspecified, the function chooses some default value
    x = librosa.stft(waveform)
    xDb = librosa.amplitude_to_db(np.abs(x))

    return xDb

def __match_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

#def normalize_wav_file(wav_file, target_dBFS=0):
#    sound = AudioSegment.from_wav(wav_file)
#    sound = __match_amplitude(sound, target_dBFS)
#    sound.export(wav_file, format="wav")
    
    
