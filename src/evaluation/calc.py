import pandas as pd

def count_organisms(df):
    """
    counts detected objects in each picture (grouping by time and id)

    returns a series object
    """
    return df.groupby(['time','id']).size()

def id_average(df, freq='D'):
    """
    uses Pandas Grouper to group based on a time interval. Very useful 
    if multiple images per day have been recorded

    returns dataframe or series depending on input
    """
    return df.groupby([pd.Grouper(freq=freq, level='time'), 'id']).mean()


def id_max(df, freq='D'):
    """
    uses Pandas Grouper to group based on a time interval. Very useful 
    if multiple images per day have been recorded

    returns dataframe or series depending on input
    """
    return df.groupby([pd.Grouper(freq=freq, level='time'), 'id']).max()
