###########################################################################################################
# THIS CONTAINS LOOK UP TABLES FOR OTHER FUNCTIONS TO MINIMIZE THERE SIZE AND TO MAKE SHARING CODE EASIER #
###########################################################################################################

clinical_data = {
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


clinical_iterables = {
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

data_cipher = {
        'recording_locations':  {'PV': 0, 'TV': 1, 'AV': 2, 'MV': 3, 'Phc': 4},
        'age':                  {'Neonate': 2, 'Infant': 26, 'Child': 6*52, 'Adolescent': 15*52, 'Young Adult': 20*52}, #represent each age group as the approximate number of weeks for the middle of the age group
        'sex':                  {'Male': 0, 'Female': 1},
        'pregnancy_status':     {'True': 1, 'False': 0},
        'murmur':               {'Present': 1, 'Absent': 0, 'Unknown': 2},
        'murmur_locations':     {'PV': 0, 'TV': 1, 'AV': 2, 'MV': 3, 'Phc': 4},
        'most_audible_location':{'PV': 0, 'TV': 1, 'AV': 2, 'MV': 3, 'Phc': 4},
        'sys_mur_timing':       {'Early-systolic': 0, 'Holosystolic': 1, 'Mid-systolic': 2, 'Late-systolic': 3},
        'sys_mur_shape':        {'Crescendo': 0, 'Decrescendo': 1, 'Diamond': 2, 'Plateau': 3},
        'sys_mur_pitch':        {'Low': 0, 'Medium': 1, 'High': 2},
        'sys_mur_grading':      {'I/VI': 0, 'II/VI': 1, 'III/VI': 2},
        'sys_mur_quality':      {'Blowing': 0, 'Harsh': 1, 'Musical': 2},
        'dia_mur_timing':       {'Early-diastolic': 0, 'Holodiastolic': 1, 'Mid-diastolic': 2},
        'dia_mur_shape':        {'Crescendo': 0, 'Decrescendo': 1, 'Diamond': 2, 'Plateau': 3}, #note: only decresendo and plateau are actually used, other items are included for consistency with 'systolic murmur shape'
        'dia_mur_pitch':        {'Low': 0, 'Medium': 1, 'High': 2},
        'dia_mur_grading':      {'I/IV': 0, 'II/IV': 1, 'III/IV': 2},
        'dia_mur_quality':      {'Blowing': 0, 'Harsh': 1, 'Musical': 2}, #note: only blowing and harsh are actually used, other items are included for consistency with 'systolic murmur quality'
        'outcome':              {'Abnormal': 0, 'Normal': 1}
    }