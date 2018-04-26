import requests

class CryptonatorApiService(object):

    def __init__(self):
        self._base_url = "https://api.cryptonator.com/api"
        self._endpoints = {
            "ticker": "/ticker/%s",
            "tickerfull": "/full/%s",
            "currency": "/currencies"
        }
        self._cache = {}

    def add_cache_item(self, k, v):
        self._cache[k] = v

    def get_cache_item(self, endpoint, nocache=False):
        if endpoint in self._cache and not nocache:
            return self._cache[endpoint]
        else:
            req_response = requests.get(endpoint)
            print(req_response.json())
            if req_response.status_code == 200:
                ret = req_response.json()
                self.add_cache_item(endpoint, ret)
                return ret

    def get_ticker_data_full(self, pair):
        return self.get_cache_item((self._base_url + self._endpoints["tickerfull"]) % pair)

    def get_currency_list(self):
        currency_list = self.get_cache_item(self._base_url + self._endpoints["currency"])
        return currency_list

    def get_currency_list_symbols(self):
        currency_list = self.get_currency_list()
        currency_list_symbols = [currency["code"] for currency in currency_list["rows"]]
        return currency_list_symbols


if __name__ == "__main__":
    TestCryptonatorService = CryptonatorApiService()
    print(TestCryptonatorService.get_currency_list())
    print(TestCryptonatorService.get_currency_list_symbols())
