import requests

class TindieOrdersAPI:
    def __init__(self, username, api_key):
        self.usr = username
        self.api = api_key
    def get_orders_json(self, shipped = None):
        url = 'https://www.tindie.com/api/v1/order/?format=json&api_key='+self.api+'&username='+self.usr
        if shipped!=None:
            if type(shipped)!=bool:
                raise ValueError("shipped must be True, False, or None.")
            url+='&shipped='
            if shipped:
                url+='true'
            else:
                url+='false'
        return requests.get(url).json()
    
