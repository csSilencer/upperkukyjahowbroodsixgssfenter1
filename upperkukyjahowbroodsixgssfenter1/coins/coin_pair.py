from .generic_coin import GenericCoin

class CoinPair(object):

    def __init__(self, Coin1, Coin2):
        self._c1 = Coin1
        self._c2 = Coin2

    def __str__(self):
        return "%s-%s" % (str(self._c1), str(self._c2))

    def __eq__(self, coinpairstr):
        return "%s-%s" % (str(self._c1), str(self._c2)) == coinpairstr \
               or "%s-%s" % (str(self._c2), str(self._c1)) == coinpairstr

if __name__ == "__main__":
    coin1 = GenericCoin("Bitcoin", "BTC")
    coin2 = GenericCoin("Ehtereum", "ETH")
    coinpair = CoinPair(coin1, coin2)
    print(coinpair)
    print("ETH-BTC" == coinpair)
    print("BTC-ETH" == coinpair)
