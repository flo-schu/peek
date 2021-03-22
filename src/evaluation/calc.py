import pandas as pd

def count_organisms(df):
    """
    counts detected objects in each picture (grouping by time and id)

    returns a series object
    """
    agg_df = df.groupby(['time','id']).size().to_frame()
    agg_df = agg_df.rename(columns={0:'count'})
    return agg_df

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