import requests, datetime, time

# EXPIRES_TIME defines the time (in seconds) that a cached order list is kept.
# Note that TindieOrdersAPI.get_orders makes a new request to Tindie's server and DOES NOT us the cache.

EXPIRES_TIME = 3600 # 3600s = 1h

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
        # key is 'shipped' argument
        self.cache = {False:None, True:None, None:None}
    def get_orders_json(self, shipped = None):
        '''Returns decoded JSON object from Tindie's Orders API'''
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
        '''Returns a list of order objects'''
        result = []
        for i in self.get_orders_json(shipped)['orders']:
            result.append(TindieOrder(i))
        self.cache[shipped] = [time.time()+EXPIRES_TIME, result]
        return result
    def _get_cache_(self, shipped = None):
        elem = self.cache[shipped]
        if elem==None or elem[0]<time.time():
            return self.get_orders(shipped)
        return elem[1]
    def get_last_order(self):
        return self._get_cache_()[0]
    def average_order_revenue(self, limit = 20):
        '''Returns average order payout, including shipping
Limit is the maximum number of orders to include, newest orders first.'''
        num_orders = 0
        amt_revenue = 0
        for i in self._get_cache_():
            amt_revenue += i.seller_payout
            num_orders += 1
            if limit!=None and num_orders>=limit:
                break
        return amt_revenue/num_orders
    def average_order_shipping(self, limit = 20):
        '''Returns average order shipping cost
Limit is the maximum number of orders to include, newest orders first.'''
        num_orders = 0
        amt_shipping = 0
        for i in self._get_cache_():
            amt_shipping += i.shipping_cost
            num_orders += 1
            if limit!=None and num_orders>=limit:
                break
        return amt_shipping/num_orders
    def average_order_timedelta(self, limit = 20):
        '''Returns average time between orders as a datetime.timedelta
Limit is the maximum number of orders to include, newest orders first.'''
        orders = self._get_cache_()
        timing = datetime.timedelta()
        num_orders = 0
        ls_time = orders.pop(0).date
        for i in orders:
            timing += ls_time - i.date
            ls_time = i.date
            num_orders += 1
            if limit!=None and num_orders>=limit:
                break
        return timing/num_orders
