import os
import numpy as np
import tensorflow as tf
from typing import Sequence, Optional, Union
import math
import helpers.input_processor as ip
import polars as pl
import matplotlib.pyplot as plt
import librosa
import tensorflow_io as tfio
import copy

def audioDatasetFromList(

):
    pass

def validateInputs(
    filePaths, labels, startTimes, endTimes, batchSize, duration, sr, augmentData
):
    def checkType(param, paramName, *allowedTypes):
        '''Checks if the specified parameter has the correct type, otherwise raises an error'''
        containsNone = None in allowedTypes
        if containsNone:
            # Remove None from list of types to check for
            allowedTypes = tuple(filter(lambda item: item is not None, allowedTypes))
            if param is None:
                return True

        if not isinstance(param, allowedTypes):
            allowedTypesPrintout = ', '.join([f'`{allowedType.__name__}`' for allowedType in allowedTypes])
            if containsNone:
                allowedTypesPrintout = allowedTypesPrintout + ', `None`'
            raise ValueError(
                f'`{paramName}` argument must be one of {allowedTypesPrintout}. '
                f'Received: {paramName}={param}'
            )

    # Check type of each parameter
    checkType(filePaths, 'filePaths', list, tuple)
    checkType(labels, 'labels', list, tuple)
    checkType(startTimes, 'startTimes', list, tuple, None)
    checkType(endTimes, 'endTimes', list, tuple, None)
    checkType(batchSize, 'batchSize', int, None)
    checkType(duration, 'duration', int, float)
    checkType(sr, 'sr', int)
    checkType(augmentData, 'augmentData', bool)

    # Check that data has consistent shape
    cols = [x for x in [filePaths, labels, startTimes, endTimes] if x is not None]
    if any(len(col)!=len(cols[0]) for col in cols):
        raise ValueError(
            '`filePaths`, `labels`, `startTimes`, and `endTimes` (if specified) '
            'must have equal lengths. '
            f'Received arguments with lengths: {[len(col) for col in cols]}'
        )
    
    # Check that startTime and endTime are either both specified or both unspecified (assuming both are either a sequence of float or None)
    if type(startTimes)!=type(endTimes):
        raise ValueError(
            '`startTimes` and `endTimes` arguments must either both be specified or both be None. '
            f'Received: startTimes={startTimes}, endTimes={endTimes}'
        )
    
    # Check that batch size is not larger than the total amount of data
    if batchSize is not None and batchSize > len(filePaths):
        raise ValueError(
            '`batchSize` cannot be larger than the length of `filePaths`. '
            f'Received: batchSize={batchSize}, len(filePaths)={len(filePaths)}'
        )