import requests


class CoinMarketCapApiService(object):

    def __init__(self):
        self._base_url = "https://api.coinmarketcap.com/v1/"
        self._endpoints = {
            "ticker": "/ticker/%s",
        }
        self._cache = {}

    def add_cache_item(self, k, v):
        self._cache[k] = v

    def get_cache_item(self, endpoint, nocache=False):
        if endpoint in self._cache and not nocache:
            return self._cache[endpoint]
        else:
            req_response = requests.get(endpoint)
            if req_response.status_code == 200:
                ret = req_response.json()
                self.add_cache_item(endpoint, ret)
                return ret

    # TODO: Use some sort of url generator api to stop building strings as such

    def get_top_coin_market_cap(self, start=0, limit=100, convert="USD"):
        top_coins = self.get_cache_item(self._base_url + self._endpoints["ticker"] %
                                        ("?start=%s&limit=%s&convert=%s" % (start, limit, convert)))
        return top_coins

    def get_top_coin_market_cap_symbols(self, start=0, limit=100, convert="USD"):
        top_coins = self.get_top_coin_market_cap(start, limit, convert)
        top_coins_symbols = [coin["symbol"] for coin in top_coins]
        return top_coins_symbols


if __name__ == "__main__":
    TestCMService = CoinMarketCapApiService()
    print(TestCMService.get_top_coin_market_cap())
    print(TestCMService.get_top_coin_market_cap_symbols())
    # print(TestCMService._cache)
