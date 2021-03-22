import numpy as np
import pandas as pd

def count_organisms(df, groups=['time','id']):
    """
    counts detected objects in each picture (grouping by time and id)

    returns a series object
    """
    df = df.groupby(groups).size().to_frame()
    df = df.rename(columns={0:'count'})
    return df

def length_width_ratio(df):
    """
    calculate the length/width ratio. This will be used for determining
    if an organism is Culex or Daphnia
    """
    df.loc[:, "lw_ratio"] = df.loc[:, 'len_major'] / df.loc[:, 'len_minor']
    return df

def classify_by_lwratio(df, threshold):
    df.loc[:, "label_auto"] = np.where(df.loc[:, "lw_ratio"] < threshold, "Daphnia Magna", "Culex Pipiens, larva")
    return df

def select_by_area(df, threshold):
    df = df.query('area > @threshold')
    return df.copy()

def culex_by_angle(df, threshold):
    """
    culex will be mirrored on the water surface. However, using an angle
    will probably also select culex in the water
    """
    pass

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


class Algorithms:
    @staticmethod
    def count_and_average_over_id(data):
        data = count_organisms(data)
        data = id_average(data)
        return data

    @staticmethod
    def filter_area_classify_lwratio(data, area_threshold, lw_threshold, groups):
        data = select_by_area(data, area_threshold)
        data = length_width_ratio(data)
        data = classify_by_lwratio(data, lw_threshold)
        data = count_organisms(data, groups)
        print(data)
        # filtering at last
        return data