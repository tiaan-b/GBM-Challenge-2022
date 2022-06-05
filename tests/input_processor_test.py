import helpers.input_processor as ip
import delayed_assert 
data_dir = "src/data/raw_training/training_data"

# if we ingest data twice we should get the same data
def test_data_consistency():
    df = ip.ingest_data(data_dir)
    df2 = ip.ingest_data(data_dir)
    assert df.frame_equal(df2)

# check the length of the dataframe is correct
def test_data_length():
    import os
    # add up all text files in the directory
    num_files = 0
    for file in os.listdir(data_dir):
        if file.endswith(".txt"):
            num_files += 1

    # loop through all columns in the dataframe and check the length
    df = ip.ingest_data(data_dir)
    for column in df.columns:
        delayed_assert.expect(len(df[column]) == num_files)


# check that we can convert files to spectrograms
def test_files_to_spectro():
    df = ip.ingest_data(data_dir)
    spectros = ip.files_to_spectro(df['audio_files'], data_dir)
    delayed_assert.expect(len(spectros) == len(df['audio_files']))
    for i in range(len(spectros)):
        delayed_assert.expect(len(spectros[i]) == len(df['audio_files'][i]))
    


    

    