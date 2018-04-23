from generic_coin import GenericCoin
from coin_pair import CoinPair

class CoinMatrix(object):

    def __init__(self, coins):
        self.coins = coins
        #  This object will not exist without an initial matrix
        self.coin_pairs = self.initialiseCoinPairs()

    def initialiseCoinPairs(self):
        """
        Initialise the array
        :return:
        """
        coin_pairs = []

        for i in range(len(self.coins)):
            coin1 = self.coins[i]
            for j in range(i+1, len(self.coins)):
                coin2 = self.coins[j]
                coin_pairs.append(CoinPair(coin1, coin2))

        return coin_pairs

if __name__ == "__main__":
    testMatrix = CoinMatrix([GenericCoin("Bitcoin", "BTC"),
                             GenericCoin("Ethereum", "ETH"),
                             GenericCoin("Litecoin", "LTC"),
                             GenericCoin("Monero", "XMR")])
    print([str(coin) for coin in testMatrix.coin_pairs])
