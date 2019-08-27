import requests, datetime, time

class TindieProduct:
    def __init__(self, data):
        self.json_parsed = data
        self.model = data['model_number']
        self.options = data['options']
        self.qty = data['quantity']
        self.sku = data['sku']
        self.unit_price = data['price_unit']
        self.price = data['price_total']
        self.name = data['product']
        

class TindieOrder:
    def __init__(self, data):
        self.json_parsed = data
        self.date = datetime.datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%S.%f')
        self.date_shipped = datetime.datetime.strptime(data['date_shipped'], '%Y-%m-%dT%H:%M:%S.%f')
        self.products = []
        for i in data['items']:
            self.products.append(TindieProduct(i))
        self.shipped = data['shipped']
        self.refunded = data['refunded']
        self.order_number = data['number']
        self.recipient_email = data['email']
        self.recipient_phone = data['phone']
        self.address_dict = {
            'city':             data['shipping_city'],
            'country':          data['shipping_country'],
            'recipient_name':   data['shipping_name'],
            'instructions':     data['shipping_instructions'],
            'postcode':         data['shipping_postcode'],
            'service':          data['shipping_service'],
            'state':            data['shipping_state'],
            'street':           data['shipping_street']
        }
        self.address_str = data['shipping_name'] + '\n'
        self.address_str+= data['shipping_street'] + '\n'
        self.address_str+= data['shipping_city'] + ' ' + data['shipping_state'] + ' ' + data['shipping_postcode'] + '\n'
        self.address_str+= data['shipping_country']
        self.seller_payout = data['total_seller']
        self.shipping_cost = data['total_shipping']
        self.subtotal = data['total_subtotal']
        self.tindie_fee = data['total_tindiefee']
        self.cc_fee = data['total_ccfee']
        if self.shipped:
            self.tracking_code = data['tracking_code']
            self.tracking_url = data['tracking_url']
        else:
            self.tracking_code = None
            self.tracking_url = None
        
class TindieOrdersAPI:
    def __init__(self, username, api_key):
        self.usr = username
        self.api = api_key
        # avoid using server twice for same request
        self.cache = {False:None, True:None, None:None}
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
    def get_orders(self, shipped = None):
        result = []
        for i in self.get_orders_json(shipped)['orders']:
            result.append(TindieOrder(i))
        
        return result
