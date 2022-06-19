###########################################################################################################
# THIS CONTAINS LOOK UP TABLES FOR OTHER FUNCTIONS TO MINIMIZE THERE SIZE AND TO MAKE SHARING CODE EASIER #
###########################################################################################################

import copy

# we use the deepcopy function to avoid overwriting the original dict
# otherwise this creates a super hard to find bug where running the code multiple times
# will result in the output being different each time

def getClinicalData():
    clinical_data = {
            'patient_id':           [],
            'total_locations':      [],
            'sampling_frequency':   [],
            'audio_file':           [],
            'recording_location':   [],
            #begin named features
            'age':                  [],
            'sex':                  [],
            'height':               [],
            'weight':               [],
            'pregnancy_status':     [],
            'murmur_in_patient':    [],
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
    return copy.deepcopy(clinical_data)

def getClinicalIterables():
    clinical_iterables = {
        'age':                  '#Age',
        'sex':                  '#Sex',
        'height':               '#Height',
        'weight':               '#Weight',
        'pregnancy_status':     '#Pregnancy status',
        'murmur_in_patient':    '#Murmur',
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
    return copy.deepcopy(clinical_iterables)

def getCipher():
    data_cipher = {
            'recording_location':   {'nan': float('nan'), 'PV': 0.0, 'TV': 1.0, 'AV': 2.0, 'MV': 3.0, 'Phc': 4.0},
            'age':                  {'nan': float('nan'), 'Neonate': 2.0, 'Infant': 26.0, 'Child': 6*52.0, 'Adolescent': 15*52.0, 'Young Adult': 20*52.0}, #represent each age group as the approximate number of weeks for the middle of the age group
            'sex':                  {'nan': float('nan'), 'Male': 0.0, 'Female': 1.0},
            'pregnancy_status':     {'nan': float('nan'), 'True': 1.0, 'False': 0.0},
            'murmur_in_patient':    {'nan': float('nan'), 'Present': 1.0, 'Absent': 0.0, 'Unknown': 0.5},
            'murmur_in_recording':  {'nan': float('nan'), 'Present': 1.0, 'Absent': 0.0, 'Unknown': 0.5},
            'murmur_locations':     {'nan': float('nan'), 'PV': 0.0, 'TV': 1.0, 'AV': 2.0, 'MV': 3.0, 'Phc': 4.0},
            'most_audible_location':{'nan': float('nan'), 'PV': 0.0, 'TV': 1.0, 'AV': 2.0, 'MV': 3.0, 'Phc': 4.0},
            'sys_mur_timing':       {'nan': float('nan'), 'Early-systolic': 0.0, 'Holosystolic': 1.0, 'Mid-systolic': 2.0, 'Late-systolic': 3.0},
            'sys_mur_shape':        {'nan': float('nan'), 'Crescendo': 0.0, 'Decrescendo': 1.0, 'Diamond': 2.0, 'Plateau': 3.0},
            'sys_mur_pitch':        {'nan': float('nan'), 'Low': 0.0, 'Medium': 1.0, 'High': 2.0},
            'sys_mur_grading':      {'nan': float('nan'), 'I/VI': 0.0, 'II/VI': 1.0, 'III/VI': 2.0},
            'sys_mur_quality':      {'nan': float('nan'), 'Blowing': 0.0, 'Harsh': 1.0, 'Musical': 2.0},
            'dia_mur_timing':       {'nan': float('nan'), 'Early-diastolic': 0.0, 'Holodiastolic': 1.0, 'Mid-diastolic': 2.0},
            'dia_mur_shape':        {'nan': float('nan'), 'Crescendo': 0.0, 'Decrescendo': 1.0, 'Diamond': 2.0, 'Plateau': 3.0}, #note: only decresendo and plateau are actually used, other items are included for consistency with 'systolic murmur shape'
            'dia_mur_pitch':        {'nan': float('nan'), 'Low': 0.0, 'Medium': 1.0, 'High': 2.0},
            'dia_mur_grading':      {'nan': float('nan'), 'I/IV': 0.0, 'II/IV': 1.0, 'III/IV': 2.0},
            'dia_mur_quality':      {'nan': float('nan'), 'Blowing': 0.0, 'Harsh': 1.0, 'Musical': 2.0}, #note: only blowing and harsh are actually used, other items are included for consistency with 'systolic murmur quality'
            'outcome':              {'nan': float('nan'), 'Abnormal': 0.0, 'Normal': 1.0},
            'campaign':             {'nan': float('nan'), 'CC2014': 0.0, 'CC2015': 1.0}
        }
    return copy.deepcopy(data_cipher)