import time
import hmac
import hashlib
from telegram import message
from sys import path, exc_info
from os.path import abspath, join, dirname


base_dir = abspath(join(dirname(__file__), "../../"))
path.append(base_dir)

from binance.um_futures import UMFutures
from decimal import Decimal
from requests import get


# To get login key
def UMF_key(key, secret):
    try:
        k = UMFutures(key, secret)
        return k
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while getting the login key.')

# To get balances of all the symbols
def UMF_balance_all(c):
    try:
        bal = {}
        k = c.account()
        for i in range(len(k['assets'])):
            if(float(k['assets'][i]['walletBalance'])>0):
                bal[k['assets'][i]['asset']] = float(k['assets'][i]['availableBalance'])
        return bal
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while getting the balance of all symbols.')

# Check Balance
def UMF_balance(c, x):
    try:
        k = c.account()
        for i in range(len(k['assets'])):
            if(k['assets'][i]['asset']==x):
                return (k['assets'][i]['availableBalance'])
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while getting the balance of the symbol.')

# Place New Order
def UMF_place_order(c, x, s, ot, q, pr = 0, tif='GTC', ps='BOTH'):
    try:
        if ((ot=='LIMIT') and ((ps=='BOTH') or (ps=='LONG') or (ps=='SHORT'))):
            r = c.new_order(symbol=x, side = s, positionSide=ps, type = ot, quantity = q, price = pr, timeInForce = tif)
        elif (ot=='MARKET' and ((ps=='BOTH') or (ps=='LONG') or (ps=='SHORT'))):
            r = c.new_order(symbol=x, side = s, positionSide=ps, type = ot, quantity = q)
        else:
            raise Exception('Order Type Error!')
        return r
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while placing a new order.')

# Query an Order
def UMF_query_order(c, x, timestamp, oid = 0, cOid = 0, recvWindow = 0):
    try:
        r = c.query_order(symbol = x, orderId = oid, clientOrderId = cOid, timestamp = timestamp)
        return r
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while querying order.')

# Get Open Orders
def UMF_open_orders(c, x):
    try:
        r = c.get_orders(symbol=x)
        return r
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while getting the open orders.')

# Get Trade History
def UMF_order_history(c, x):
    try:
        r = c.get_all_orders(symbol = x)
        return r
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while getting the trade history.')

# Cancel a specific open order 
def UMF_delete_order(c, x, oid):
    try:
        r = c.cancel_order(symbol = x, orderId = oid)
        return r
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while cancelling the specific open order.')

# Cancel all open orders for Specific Symbol
def UMF_delete_all_orders(c, x):
    try:
        r = c.cancel_open_orders(symbol=x)
        return r
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while cancelling all open order for symbol.')

# Modify Order Alternative (Cancel Order and Place New Order Combination)
def UMF_modify_order(c, x, s, ot, q, oid, pr, tif='GTC', ps='BOTH'):
    try:
        r = c.cancel_order(symbol=x, orderId=oid)
        if ((ot == 'LIMIT') and ((ps=='BOTH') or (ps=='LONG') or (ps=='SHORT'))):
            newr = c.new_order(symbol=x, side=s, positionSide=ps, type=ot, quantity=q, price=pr, timeInForce=tif)
            return r, newr
        elif(ot == 'MARKET'):
            newr = c.new_order(symbol=x, side=s, type=ot, quantity=q)
        else:
            print(f"{err}: Invalid order type.")
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while modifying the order.')

# Change Default Leverage Settings
def UMF_modify_leverage(c, x, l):
    try:
        r = c.change_leverage(symbol=x, leverage=l)
        return r
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while changing the default leverage settings.')

# View Position mode set for the account
def UMF_get_position_mode(c):
    try:
        r = c.get_position_mode()
        return r['dualSidePosition']
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while viewing the position mode of the account.')

# Change Position Mode for the account
def UMF_change_position_mode(c, dsp):
    try:
        if UMF_get_position_mode(c) != dsp:
            if len(list(UMF_open_position(c))) == 0:
                r = c.change_position_mode(dualSidePosition=dsp)
                if r['msg'] == 'success':
                    return 'Changed'
                else:
                    return 'Failed'
            else:
                return 'Open Position'
        return 'Already set!' 
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while changing the position mode of the account.')

# View asset mode set for the account
def UMF_get_asset_mode(c):
    try:
        r = c.get_multi_asset_mode()
        return bool(r['multiAssetsMargin'])
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while viewing the asset mode of the account.')

# Change asset mode for the account
def UMF_change_asset_mode(c, mam):
    try:
        if UMF_get_asset_mode(c) != mam:
            kk = c.change_multi_asset_mode(multiAssetsMargin=str(mam))
            if kk['msg'] == 'success':
                return True
            else:
                return False
        return True
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while changing the asset mode of the account.')

# View Position Risk of the open position
def UMF_get_position_risk(c, x = ''):
    try:
        ff = c.get_position_risk()
        if x == '':
            return ff
        for i in ff:
            if i['symbol'] == x:
                return i
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while viewing the position risk of the open positions.')

# Get Leverage scale for a symbol
def UMF_get_leverage(c, mar, x):
    try:
        hh = c.leverage_brackets()
        for i in hh:
            if i['symbol'] == x:
                k = i['brackets']
                for j in k:
                    if float(mar)<= float(j['notionalCap']) and float(mar)>= float(j['notionalFloor']):
                        return float(j['initialLeverage']), float(j['maintMarginRatio'])
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while getting the leverage scale of the symbol.')

# Get quantity in order for a coin
def UMF_get_quantity(c, x, td):
    try:
        ff = c.get_position_risk(symbol=x)
        for i in ff:
            if i['positionSide'] == td:
                return abs(float(i['positionAmt']))
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while the quantity in order for coin.')

#Get precision for quantity and price
def UMF_check_precision(coin, price, quantity):
    try:
        c = UMFutures()
        data = c.exchange_info()['symbols']
        for symbols in data:
            if symbols['symbol'] == coin:
                precision = {}
                precision['price'] = Decimal(symbols['filters'][0]['tickSize'].find('1') - 1)
                price = Decimal(price).quantize(1/ 10 ** precision['price'])
                if int(float(symbols['filters'][1]['stepSize'])) == 1:
                    precision['quantity'] = Decimal(symbols['filters'][1]['stepSize'])
                    quantity = int(float(quantity))
                else:
                    precision['quantity'] = Decimal(symbols['filters'][1]['stepSize']) 
                    quantity = Decimal(quantity).quantize(precision['quantity'])
                return float(price), float(quantity)
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while getting the quantity and price precision.')

#Open positions
def UMF_open_position(c):
    try:
        g = UMF_get_position_risk(c)
        o = []
        for i in g:
            if float(i['positionAmt']) > 0:
                o.append(i)
        return o
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}\nError occured while getting open positions.')
        live_error_logs(coin_name = coin_name, initial_balance = initial_balance, base_trade_val = base_trade_val, leverage = leverage, quantity_multiplier = quantity_multiplier, grid_size_percent = grid_size_percent, profit_percent = profit_percent, exchange = exchange, klines_type = klines_type, balance = check_balance, error_msg = err)

# To get market price of the symbol
def UMF_live(coin):
    try:
        key ="https://fapi.binance.com/fapi/v1/ticker/price?symbol=" + coin
        data = get(key)
        data = data.json()
        return data['price']
    except Exception as err:
        print(f"{err}: Error occured while getting live price.")

# To get Commission Rate of Coin
def get_commission_rate(symbol, api_key, secret_key):

    endpoint_url = 'https://fapi.binance.com/fapi/v1/commissionRate'

    symbol = 'BTCUSDT'  # Replace with the trading pair you're interested in

    # Define the timestamp
    timestamp = int(time.time() * 1000)

    # Create a dictionary with the required parameters
    params = {
        'symbol': symbol,
        'timestamp': timestamp,
        # 'recvWindow': 5000,  # Optional: Adjust this value as needed or omit it
    }

    # Create a signature for the request
    query_string = '&'.join([f'{key}={params[key]}' for key in params])
    signature = hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    # Add the signature to the parameters
    params['signature'] = signature

    # Set the headers with the API key
    headers = {
        'X-MBX-APIKEY': api_key,
    }

    # Make the GET request
    response = get(endpoint_url, params=params, headers=headers)
    data = response.json()

    return float(data["makerCommissionRate"]), float(data["takerCommissionRate"])


    # coin = coin.lower()
    # url = f"https://fapi.binance.com/fapi/v1/userTrades?symbol={coin}"
    # data = get(url)
    # data = data.json()
    # return data

# To get historical data of the symbol
# def UMF_hist(coin, intrv, std, end, can, pt):
#     try:
#         c = Client()
#         r = DataFrame(c.get_historical_klines(coin ,intrv, str(std), str(end), klines_type=HistoricalKlinesType.FUTURES))
#         rt = {
#             'DateTime': to_datetime(to_numeric(r[0]), unit='ms'), 
#             'OPEN': to_numeric(r[1]), 
#             'HIGH': to_numeric(r[2]),
#             'LOW': to_numeric(r[3]),
#             'CLOSE': to_numeric(r[4])
#         }
#         if(can == 'HEIKIN-ASHI-CANDLESTICKS'):
#             y = heikinashi(rt['OPEN'], rt['HIGH'], rt['LOW'], rt['CLOSE'])
#             rt['OPEN'] = y['OPEN']
#             rt['HIGH'] = y['HIGH']
#             rt['LOW'] = y['LOW']
#             rt['CLOSE'] = y['CLOSE']
#         elif (can != 'CANDLESTICKS'):
#             raise Exception('Enter appropriate Candlesticks Type!')
#         if pt == 'OPEN':
#             t = {
#                 'DateTime': rt['DateTime'],
#                 'Price': rt['OPEN']
#             }
#         elif pt == 'CLOSE':
#             t = {
#                 'DateTime': rt['DateTime'],
#                 'Price': rt['CLOSE']
#             }
#         elif pt == 'HIGH':
#             t = {
#                 'DateTime': rt['DateTime'],
#                 'Price': rt['HIGH']
#             }
#         elif pt == 'LOW':
#             t = {
#                 'DateTime': rt['DateTime'],
#                 'Price': rt['LOW']
#             }
#         elif pt == 'AVGHL':
#             t = {
#                 'DateTime': rt['DateTime'],
#                 'Price': (rt['HIGH'] + rt['LOW'])/2
#             }
#         elif pt == 'AVGHLC':
#             t = {
#                 'DateTime': rt['DateTime'],
#                 'Price': (rt['HIGH'] + rt['LOW'] + rt['CLOSE'])/3
#             }
#         elif pt == 'AVGOHLC':
#             t = {
#                 'DateTime': rt['DateTime'],
#                 'Price': (rt['OPEN'] + rt['HIGH'] + rt['LOW'] + rt['CLOSE'])/4
#             }
#         else:
#             raise Exception('Enter appropriate Price Type!')
#         t = DataFrame(t)
#         return t
#     except Exception as err:
#         exc_type, exc_obj, exc_tb = exc_info()
#         send(f'ERROR!\nAPI: AlgoTradingServer\nFolder: Binance\nFile: um_futures.py\nFunction: UMF_hist\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}')

