# basic python test
def inc(x):
    return x + 2


def test_answer():
    assert inc(3) == 5

# check numpy works
import numpy as np
def test_numpy():
    x = np.array([1, 2, 3])
    assert x.shape == (3,)

# check polars works
import polars as pl
def test_polars():
    df = pl.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    assert df.shape == (3, 2)

# check matplotlib works
import matplotlib.pyplot as plt
def test_matplotlib():
    plt.plot([1, 2, 3])
    # check if plot was created
    assert plt.fignum_exists(1)
