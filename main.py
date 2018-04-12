import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from pprint import pprint as pp
import json

# https://python-graph-gallery.com/46-add-text-annotation-on-scatterplot/

import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import seaborn as sns

# Get the data
req_response = requests.get("https://api.cryptonator.com/api/full/btc-usd")
response_json = req_response.json()

markets = response_json["ticker"]["markets"]

# Create dataframe
df = pd.DataFrame({
    'price': [float(market["price"]) for market in markets],
    'volume': [float(market["volume"]) for market in markets],
    'group': [market["market"] for market in markets]
})

# basic plot
p1 = sns.regplot(data=df, x="price", y="volume", fit_reg=False, marker="o", color="skyblue", scatter_kws={'s':400})

# # add annotations one by one with a loop
for line in range(0,df.shape[0]):
    print("price-%s, volume-%s, market-%s" % (df.price[line], df.volume[line], df.group[line]))
    p1.text(df.price[line]+0.2, df.volume[line], df.group[line], horizontalalignment='left', size='medium', color='black', weight='semibold')


plt.show()
