from .generic_coin import GenericCoin
from services.cryptonator import CryptonatorApiService

class CoinPair(object):

    def __init__(self, Coin1, Coin2):
        self._c1 = Coin1
        self._c2 = Coin2
        self._exchange_data = self.refresh_exchange_data()

    def get_exchange_data(self):
        return str(self._exchange_data)

    def refresh_exchange_data(self):
        crypt_service = CryptonatorApiService()
        ticker_data = crypt_service.get_ticker_data_full(str(self))
        ticker_data_reversed = crypt_service.get_ticker_data_full(self.reversed_symbol())
        if ticker_data or ticker_data_reversed:
            if len(ticker_data) > len(ticker_data_reversed):
                return ticker_data
            else:
                return ticker_data_reversed
        else:
            raise Exception("No ticker data for coin pair %s" % str(self))

    def reversed_symbol(self):
        return "%s-%s" % (str(self._c2), str(self._c1))

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
