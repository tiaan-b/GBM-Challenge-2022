import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

#####################################################################
#  PURPOSE:   PRODUCES THE SPECTROGRAM OF THE SPECIFIED .WAV FILE   #
#       PARAMS:    WAV_FILE    STR     PATH TO THE .WAV FILE        #
# RETURNS:   NDARRAY OF FLOAT32 - SPECTROGRAM OF INPUTTED .WAV FILE #
#####################################################################

def wav_to_spectro(wav_file, sr=4000):
    waveform, samp_rate = librosa.load(wav_file, sr=sr) #make sure that the correct sample rate is passed as a parameters. if unspecified, the function chooses some default value
    x = librosa.stft(waveform)
    xDb = librosa.amplitude_to_db(np.abs(x))
    return xDb

# if using function in a loop, run "matplotlib.pyplot.close()" after each
# iteration to prevent multiple figures from being open at the same time.
def printSpectro(spectro, title='', sr=4000):
    fig = plt.figure()
    
    librosa.display.specshow(spectro, x_axis='s', y_axis='linear', sr=sr)

    plt.colorbar(format="%+2.f dB")

    if not title=='':
        plt.title(title)
    
    duration = plt.gca().get_xlim()[1] - plt.gca().get_xlim()[0]
    __set_width(duration/2 * 1.25)


#reshapes current matplotlib figure based on the desired length of the x axis in inches
#note: if figure has a colorbar, multiply desired width by 1.25
#adapted from https://stackoverflow.com/questions/44970010/axes-class-set-explicitly-size-width-height-of-axes-in-given-units
#PARAMS:    w       float   desired width of the x axis in inches
#           h       float   [optional] height of the figure in inches, default=5
#           ax              [optional] matplotlib axes
def __set_width(w, ax=None, h=5):
    """ w, h: width, height in inches """
    if not ax: ax=plt.gca()
    l = ax.figure.subplotpars.left
    r = ax.figure.subplotpars.right
    # t = ax.figure.subplotpars.top
    # b = ax.figure.subplotpars.bottom
    figw = float(w)/(r-l)
    # figh = float(h)/(t-b)
    # figh = plt.gcf().get_figheight()
    figh = float(h)

    ax.figure.set_size_inches(figw, figh)