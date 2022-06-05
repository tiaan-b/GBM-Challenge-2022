import helpers.audio_tools as adt

def test_wav_to_spectro():
    x = adt.wav_to_spectro("src/data/raw_training/training_data/2530_AV.wav", sr=4000)
    # check if x is a 2D array
    assert len(x.shape) == 2