import pandas as pd
import pylab
import numpy as np
from statsmodels.graphics.mosaicplot import mosaic
from itertools import product


def mekko_chart(data, names, categories, title):

    labels = list(product(names, categories))
    index = pd.MultiIndex.from_tuples(labels, names=names)

    data = pd.Series(data, index=index)
    props = lambda key: {"color": "orange" if categories[0] in key else "deepskyblue"}
    mosaic(data, gap=[0.01, 0.01], title=title, properties=props)
    
    return pylab