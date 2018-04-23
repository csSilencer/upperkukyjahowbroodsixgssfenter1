from generic_coin import GenericCoin
# from coin_pair import CoinPair # this works!
from coin_matrix import CoinMatrix

class CoinMatrixController(object):

    def get_pair_matrix(self):
        """
        In your head create a N by N array,
        where N are the coins. In a cell, i,j - We have the pair i-j.
        This cell will contain an object, whose value is the ticker for that pair i-j
        E.g. row BTC, col ETH, the cell BTC-ETH will contain the result of
        retrieve_data("BTC-ETH")

        However, in practice this would be silly and we would lead to
        duplicated results, e.g. compute BTC-BTC, BTC-ETH, ETH-BTC.

        Instead we loop over each coin symbol and construct a stateful object "Coin" for it
        Each "Coin" object will then try and create a "CoinPair" object for each other N-1 pairs.
        Obviously some pairs have already been computed, so we don't have to do them again

        A control loop will go over each Coin we have registered and update each "CoinPair"
        :return:
        """
        cms = CoinMarketCapApiService()
        cms_coins = cms.get_top_coin_market_cap()
        coins = []

        for coin in cms_coins:
            coins.append(GenericCoin(coin["name"], coin["symbol"]))

        coin_matrix = CoinMatrix(coins)
        print([str(coin) for coin in coin_matrix.coin_pairs])
        print(len(coin_matrix.coin_pairs))

if __name__ == "__main__":
    testMatrix = CoinMatrix([GenericCoin("Bitcoin", "BTC"),
                             GenericCoin("Ethereum", "ETH"),
                             GenericCoin("Litecoin", "LTC"),
                             GenericCoin("Monero", "XMR")])
    print([str(coin) for coin in testMatrix.coin_pairs])