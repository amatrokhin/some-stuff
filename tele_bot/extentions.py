import requests
import json
from config import curs, API_KEY


class APIException(Exception):                                     #class for user-made exceptions
    pass


class CurrencyConverter:
    @staticmethod
    def get_price(base: str, quote: str, amount: str):             #chech for user mistakes and make a request
        if quote == base:
            raise APIException(f'Не возможно перевести одинаковые валюты {base}')

        try:
            curs[base.upper()]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту {base}')

        try:
            curs[quote.upper()]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту {quote}')

        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать количество {amount}')

        if amount <= 0:
            raise APIException(f'Не удалось обработать количество {amount}')

        #r = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
        #currencies = r.json()
        #if base
        url = f"https://api.apilayer.com/currency_data/convert?to={quote.upper()}&from={base.upper()}&amount={amount}"
        #r = requests.request("GET", url, headers={'apikey': API_KEY})
        r = requests.get(url, headers={'apikey': API_KEY})
        total_quote = json.loads(r.content)['result']

        return total_quote