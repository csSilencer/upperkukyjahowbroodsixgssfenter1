import matplotlib.pylab as plt
import pandas as pd
import requests
import seaborn as sns
from services.coinmarketcap import CoinMarketCapApiService
from services.cryptonator import CryptonatorApiService
from coins.generic_coin import GenericCoin
from coins.coin_matrix import CoinMatrix

class ArbitrageBot(object):
    """
    Initial bot class with methods to
    TODO: https://python-graph-gallery.com/46-add-text-annotation-on-scatterplot/
    """

    def __init__(self, api_url="https://api.cryptonator.com/api/full/btc-usd"):
        self.api_url = api_url

    @staticmethod
    def retrieve_data(api_url):
        req_response = requests.get(api_url)
        response_json = req_response.json()

        # TODO move "ticker" and "markets" out to generalise method
        return response_json["ticker"]["markets"]

    @staticmethod
    def create_dataframe(markets):
        # TODO generalise
        return pd.DataFrame({
            'price': [float(market["price"]) for market in markets],
            'volume': [float(market["volume"]) for market in markets],
            'group': [market["market"] for market in markets]
        })

    def plot_spreads(self):
        markets = self.retrieve_data(self.api_url)
        df = self.create_dataframe(markets)
        # basic plot
        p1 = sns.regplot(data=df, x="price", y="volume", fit_reg=False, marker="o", color="skyblue",
                         scatter_kws={'s': 400})

        # # add annotations one by one with a loop
        for line in range(0, df.shape[0]):
            print("price-%s, volume-%s, market-%s" % (df.price[line], df.volume[line], df.group[line]))
            p1.text(df.price[line] + 0.2, df.volume[line], df.group[line], horizontalalignment='left', size='medium',
                    color='black', weight='semibold')

        plt.show()

if __name__ == "__main__":
    TestCMService = ArbitrageBot()
    TestCMService.get_pair_matrix()
