import pandas as pd
import pylab
import numpy as np
from statsmodels.graphics.mosaicplot import mosaic
from itertools import product

def mekko_chart(data, options, names, title, props):
    """
    Makes a mekko chart
    """
    ## Changing the order of this will change the axis
    matrix = list(product(names, options))
    index = pd.MultiIndex.from_tuples(matrix, names=options)
    
    data_series = pd.Series(data, index=index)
    mosaic(data_series, gap=[0.01, 0.01], title=title, properties=props)
    
    return pylab