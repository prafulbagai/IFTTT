from __future__ import division
from c26_smartbulb.local_settings import *
import requests
import json
import re

class Stock(object):
    def __init__(self):
        pass

    def _make_request(self, company_symbol):
        url = YAHOO_STOCKS_URL.format(company_symbol=company_symbol)
        response = requests.get(url)
        if not response.ok:
            return {}

        response = re.split('[\(\)]', response.text)
        try:
            return json.loads(response[1])
        except Exception,e:
            print str(e)
            return {}

    def _parse_data(self, response):
        current_stock = response.get('series')[-1].get('open')
        prev_stock_close = response.get('meta').get('previous_close')
        up_down = (current_stock - prev_stock_close)
        change_percent = (up_down / prev_stock_close) * 100
        return {
            'current_stock': current_stock,
            'prev_stock_close': prev_stock_close,
            'up_down': up_down,
            'change_percent': change_percent
        }

    def get_stock(self, company_symbol, stock_code):
        company_symbol = company_symbol.upper() + '.' + stock_code.upper()
        response = self._make_request(company_symbol)
        if response:
            return self._parse_data(response)
        else:
            return {}