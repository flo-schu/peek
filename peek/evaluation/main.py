from evaluation.calc import Algorithms as algs
from evaluation.plot import Viz as viz
import matplotlib.pyplot as plt

def save(
    data,
    path,
    algorithm=None,
    algoargs=(),
    sample_id='all', 
    date='all', 
    img_num='all'
    ):
    """
    save data (can be raw just after collection or after furthe processing
    as determined by algorithm) as CSV file
    """
    data = data.collect(sample_id, date, img_num)

    # 2. processing steps
    if algorithm is not None:
        algorithm = getattr(algs, algorithm)
        data = algorithm(data, *algoargs)

    data.to_csv(path)

def analyse(
    data,
    algorithm,
    plot,
    algoargs=(),
    plotargs={},
    sample_id='all', 
    date='all', 
    img_num='all'
    ):
    """
    TS analysis always consists of three steps:
    1. data import by collect function (later merge and other imports)
    2. steps algorithm executes a series of processing steps which can 
        be reused
    3. plot calls a plot function
    """
    # 1. collect data
    data = data.collect(sample_id, date, img_num)
    
    # 2. processing steps
    algorithm = getattr(algs, algorithm)
    data = algorithm(data, **algoargs)
    # 3. plot 
    plot = getattr(viz, plot)
    plot(data, **plotargs)

    # save plot
    plt.savefig("plots/timeseries/"+sample_id+".png")
    plt.show()
