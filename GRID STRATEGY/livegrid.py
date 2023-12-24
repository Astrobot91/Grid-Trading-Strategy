import time
import json
import websocket
import datetime
import um_futures_exp as futures
from telegram import message
from sys import path, exc_info, exit
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process, Manager, Queue
from db_append import live_trade_execution, live_error_logs, live_generate_report


trade_direction_val_long = "LONG"
trade_direction_val_short = "SHORT"
trade_signal_val_buy = "BUY"
trade_signal_val_sell = "SELL"

live_price_queue = Queue()
data_manager = Manager()

buy_quantity = data_manager.list()
sell_quantity = data_manager.list()
entry_time_buy = data_manager.list()
entry_time_sell = data_manager.list()
trade_info_buy = data_manager.list()
trade_info_sell = data_manager.list()
unprecise_buy_quantity = data_manager.list() 
unprecise_sell_quantity = data_manager.list()

processExecuter = ProcessPoolExecutor(max_workers = 4)

def fetch_live_price(coin_name):

    coin_name = coin_name.lower()

    def on_message(ws, message):
        data = json.loads(message)
        if 'p' in data:
            live_price_queue.put(float(data["p"]))

    def on_error(ws, error):
        print(f"WebSocketEror: {error}")

    def on_open(ws):
        subscribe_msg = {
            "method" : "SUBSCRIBE",
            "params" : [
                f"{coin_name}@trade",
            ],
            "id" : 1
        }
        ws.send(json.dumps(subscribe_msg))
        print("WebSocket Connection Established.")

    def on_close(ws, close_status_code, close_msg):
        print("WebSocket Closed.\nReconnecting...")
        reconnect()

    def reconnect():
        while True:
            try:
                print("Attempting to reconnect...")
                ws = websocket.WebSocketApp(url = end_point, on_message = on_message, on_open = on_open, on_close = on_close, on_error = on_error)
                ws.run_forever()
            except Exception as err:
                print(f"Reconnection failed: {err}")
                time.sleep(5)

    end_point = f"wss://stream.binance.com:9443/ws"
    ws = websocket.WebSocketApp(url = end_point, on_message = on_message, on_open = on_open, on_close = on_close)
    ws.run_forever()

def place_long_buy_order(login_key, trade_price, maker_brokerage, margin, leverage, coin_name, order_type, initial_balance, base_trade_value, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, long_quantity, short_quantity, pnl_counter, pnl_percent_counter, net_brokerage):
    if trade_price not in trade_info_buy:
        try:
            price = round(trade_price, 1)
            amount = margin * leverage
            unprecise_quantity = amount / price
            precise_quantity = round(unprecise_quantity, 3)
            orderResponseBuy = futures.UMF_place_order(c = login_key, x = coin_name, s = trade_signal_val_buy, ot = order_type, q = precise_quantity, pr = price, tif = "GTC", ps = trade_direction_val_long)
            orderHistory = futures.UMF_query_order(c = login_key, x = coin_name, oid = orderResponseBuy["orderId"], timestamp = orderResponseBuy["updateTime"])
            time_val = datetime.datetime.now()
            holding_time = pnl = pnl_percent = 0
            long_quantity.value += precise_quantity
            brokerage = maker_brokerage * amount
            net_brokerage.value += brokerage
            trade_info_buy.append(float(orderHistory["avgPrice"]))
            print(f"TRADE INFO BUY: {trade_info_buy}")
            buy_quantity.append(precise_quantity)
            entry_time_buy.append(time_val)
            unprecise_buy_quantity.append(unprecise_quantity)
            check_balance = float(futures.UMF_balance(c = login_key, x = "USDT"))
            return (orderResponseBuy, time_val, float(orderHistory["avgPrice"]), precise_quantity, short_quantity.value, long_quantity.value, float(orderHistory["cumQuote"]), holding_time, pnl, pnl_percent, pnl_counter, pnl_percent_counter, brokerage, net_brokerage.value, check_balance)
        except Exception as err:
            exc_type, exc_obj, exc_tb = exc_info()
            check_balance = float(futures.UMF_balance(c = login_key, x = "USDT"))
            message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}')
            live_error_logs(coin_name = coin_name, initial_balance = initial_balance, base_trade_val = base_trade_value, leverage = leverage, quantity_multiplier = quantity_multiplier, grid_size_percent = grid_size_percent, profit_percent = profit_percent, exchange = exchange, klines_type = klines_type, balance = check_balance, error_msg = err)
            exit()
    else:
        return 0

def place_short_sell_order(login_key, trade_price, maker_brokerage, margin, leverage, coin_name, order_type, initial_balance, base_trade_value, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, long_quantity, short_quantity, pnl_counter, pnl_percent_counter, net_brokerage):
    if trade_price not in trade_info_sell:
        try:
            price = round(trade_price, 1)
            amount = margin * leverage
            unprecise_quantity = amount / price
            precise_quantity = round(unprecise_quantity, 3)
            orderResponseSell = futures.UMF_place_order(c = login_key, x = coin_name, s = trade_signal_val_sell, ot = order_type, q = precise_quantity, pr = price, tif = "GTC", ps = trade_direction_val_short)
            orderHistory = futures.UMF_query_order(c = login_key, x = coin_name, oid = orderResponseSell["orderId"], timestamp = orderResponseSell["updateTime"])
            time_val = datetime.datetime.now()
            holding_time = pnl = pnl_percent = 0
            short_quantity.value += precise_quantity
            brokerage = maker_brokerage * amount
            net_brokerage.value += brokerage
            trade_info_sell.append(float(orderHistory["avgPrice"]))
            print(f"TRADE INFO SELL: {trade_info_sell}")
            sell_quantity.append(precise_quantity)
            entry_time_sell.append(time_val)
            unprecise_sell_quantity.append(unprecise_quantity)
            check_balance = float(futures.UMF_balance(c = login_key, x = "USDT"))
            return (orderResponseSell, time_val, float(orderHistory["avgPrice"]), precise_quantity, short_quantity.value, long_quantity.value, float(orderHistory["cumQuote"]), holding_time, pnl, pnl_percent, pnl_counter, pnl_percent_counter, brokerage, net_brokerage.value, check_balance)
        except Exception as err:
            exc_type, exc_obj, exc_tb = exc_info()
            check_balance = float(futures.UMF_balance(c = login_key, x = "USDT"))
            message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}')
            live_error_logs(coin_name = coin_name, initial_balance = initial_balance, base_trade_val = base_trade_value, leverage = leverage, quantity_multiplier = quantity_multiplier, grid_size_percent = grid_size_percent, profit_percent = profit_percent, exchange = exchange, klines_type = klines_type, balance = check_balance, error_msg = err)
            exit()
    else:
        return 0

def live_grid(public_key, secret_key, coin_name, exchange, klines_type, base_trade_value, leverage, profit_percent, quantity_multiplier, grid_size_percent, order_type):

    long_quantity = data_manager.Value('d', 0)
    short_quantity = data_manager.Value('d', 0)
    net_brokerage = data_manager.Value('d', 0)

    trade_flag = 0
    grid_size = 0
    pnl_counter = 0
    pnl_percent_counter = 0

    tick = datetime.datetime.now()
    margin = base_trade_value * quantity_multiplier

    login_key = futures.UMF_key(key = public_key, secret = secret_key)
    position_mode = futures.UMF_change_position_mode(c = login_key, dsp = "true")
    set_leverage = futures.UMF_modify_leverage(c = login_key, x = coin_name, l = leverage) 
    maker_brokerage, taker_brokerage = futures.get_commission_rate(symbol = coin_name, api_key = public_key, secret_key = secret_key)
    initial_balance = float(futures.UMF_balance(c = login_key, x = "USDT"))

    process0 = Process(target = fetch_live_price, args = (coin_name,))
    process0.start()

    while True:
        try:
            live_price = live_price_queue.get()
            if trade_flag == 0:
                entry_value = live_price
                grid_size = round((entry_value * grid_size_percent), 2)
                buy_order_response = processExecuter.submit(place_long_buy_order, login_key, entry_value, maker_brokerage, margin, leverage, coin_name, order_type, initial_balance, base_trade_value, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, long_quantity, short_quantity, pnl_counter, pnl_percent_counter, net_brokerage)
                sell_order_response = processExecuter.submit(place_short_sell_order, login_key, entry_value, maker_brokerage, margin, leverage, coin_name, order_type, initial_balance, base_trade_value, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, long_quantity, short_quantity, pnl_counter, pnl_percent_counter, net_brokerage)
                buy_order_response = buy_order_response.result()
                sell_order_response = sell_order_response.result()
                buy_price = trade_info_buy.pop()
                sell_price = trade_info_sell.pop()
                average_price = round(((buy_price + sell_price) / 2), 2)
                trade_info_buy.append(average_price)
                trade_info_sell.append(average_price)
                if buy_order_response:
                    processExecuter.submit(live_trade_execution, coin_name, "LIVE", initial_balance, base_trade_value, leverage, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, buy_order_response[0], buy_order_response[0]["type"], buy_order_response[1], buy_order_response[2], trade_direction_val_long, trade_signal_val_buy, buy_order_response[3], buy_order_response[4], buy_order_response[5], margin, buy_order_response[6], buy_order_response[7], buy_order_response[8], buy_order_response[9], buy_order_response[10], buy_order_response[11], buy_order_response[12], buy_order_response[13], buy_order_response[14])
                if sell_order_response:
                    processExecuter.submit(live_trade_execution, coin_name, "LIVE", initial_balance, base_trade_value, leverage, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, sell_order_response[0], sell_order_response[0]["type"], sell_order_response[1], sell_order_response[2], trade_direction_val_short, trade_signal_val_sell, sell_order_response[3], sell_order_response[4], sell_order_response[5], margin, sell_order_response[6], sell_order_response[7], sell_order_response[8], sell_order_response[9], sell_order_response[10], sell_order_response[11], sell_order_response[12], sell_order_response[13], sell_order_response[14])
                tock = datetime.datetime.now()
                check_balance = float(futures.UMF_balance(c = login_key, x = "USDT"))
                processExecuter.submit(live_generate_report, "Running", coin_name, exchange, klines_type, initial_balance, base_trade_value, leverage, quantity_multiplier, grid_size_percent, profit_percent, tick, tock)
                trade_flag = 1

                print(f"TRADE INFO BUY - AVG: {trade_info_buy}")
                print(f"TRADE INFO SELL - AVG: {trade_info_sell}")
                print(f"CURRENT GRID SIZE: {grid_size}")

            elif trade_flag == 1:
                if live_price >= (trade_info_buy[-1] + grid_size):
                    price = round((trade_info_buy[-1] + grid_size), 1)

                    print(f"TARGET LONG-SELL PRICE: {price}")

                    precise_quantity = buy_quantity[-1]                  
                    orderResponseSell = futures.UMF_place_order(c = login_key, x = coin_name, s = trade_signal_val_sell, ot = order_type, q = precise_quantity, pr = price, tif = "GTC", ps = trade_direction_val_long)
                    orderHistory = futures.UMF_query_order(c = login_key, x = coin_name, oid = orderResponseSell["orderId"], timestamp = orderResponseSell["updateTime"])
                    trade_info_buy.pop()
                    buy_quantity.pop()
                    last_time = entry_time_buy.pop()
                    unprecise_buy_quantity_val = unprecise_buy_quantity.pop()
                    buy_order_response = processExecuter.submit(place_long_buy_order, login_key, price, maker_brokerage, margin, leverage, coin_name, order_type, initial_balance, base_trade_value, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, long_quantity, short_quantity, pnl_counter, pnl_percent_counter, net_brokerage)
                    sell_order_response = processExecuter.submit(place_short_sell_order, login_key, price, maker_brokerage, margin, leverage, coin_name, order_type, initial_balance, base_trade_value, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, long_quantity, short_quantity, pnl_counter, pnl_percent_counter, net_brokerage)
                    buy_order_response = buy_order_response.result()
                    sell_order_response = sell_order_response.result()
                    new_unprecise_quantity = (margin * leverage) / price
                    pnl = (unprecise_buy_quantity_val - new_unprecise_quantity) * price
                    pnl_percent = (pnl / initial_balance) * 100
                    pnl_counter += pnl
                    pnl_percent_counter += pnl_percent
                    exit_margin = pnl + margin
                    amount = (margin * leverage) + pnl
                    long_quantity.value -= precise_quantity
                    time_val = datetime.datetime.now()
                    holding_time = time_val - last_time
                    brokerage = taker_brokerage * amount
                    net_brokerage.value += brokerage
                    check_balance = float(futures.UMF_balance(c = login_key, x = "USDT"))
                    buy_price = trade_info_buy.pop()
                    sell_price = trade_info_sell.pop()
                    average_price = round(((buy_price + sell_price) / 2), 2)
                    trade_info_buy.append(average_price)
                    trade_info_sell.append(average_price)
                    grid_size = round((abs(trade_info_sell[-1] - trade_info_sell[-2])), 2)
                    processExecuter.submit(live_trade_execution, coin_name, "LIVE", initial_balance, base_trade_value, leverage, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, orderResponseSell, orderResponseSell["type"], time_val, orderHistory["avgPrice"], trade_direction_val_long, trade_signal_val_sell, precise_quantity, short_quantity.value, long_quantity.value, exit_margin, amount, holding_time, pnl, pnl_percent, pnl_counter, pnl_percent_counter, brokerage, net_brokerage.value, check_balance)
                    processExecuter.submit(live_generate_report, "Running", coin_name, exchange, klines_type, initial_balance, base_trade_value, leverage, quantity_multiplier, grid_size_percent, profit_percent, tick, time_val)
                    if buy_order_response:
                        processExecuter.submit(live_trade_execution, coin_name, "LIVE", initial_balance, base_trade_value, leverage, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, buy_order_response[0], buy_order_response[0]["type"], buy_order_response[1], buy_order_response[2], trade_direction_val_long, trade_signal_val_buy, buy_order_response[3], buy_order_response[4], buy_order_response[5], margin, buy_order_response[6], buy_order_response[7], buy_order_response[8], buy_order_response[9], buy_order_response[10], buy_order_response[11], buy_order_response[12], buy_order_response[13], buy_order_response[14])
                    if sell_order_response:
                        processExecuter.submit(live_trade_execution, coin_name, "LIVE", initial_balance, base_trade_value, leverage, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, sell_order_response[0], sell_order_response[0]["type"], sell_order_response[1], sell_order_response[2], trade_direction_val_short, trade_signal_val_sell, sell_order_response[3], sell_order_response[4], sell_order_response[5], margin, sell_order_response[6], sell_order_response[7], sell_order_response[8], sell_order_response[9], sell_order_response[10], sell_order_response[11], sell_order_response[12], sell_order_response[13], sell_order_response[14])
                    processExecuter.submit(live_generate_report, "Running", coin_name, exchange, klines_type, initial_balance, base_trade_value, leverage, quantity_multiplier, grid_size_percent, profit_percent, tick, time_val)

                    print(f"SQUAREDOFF AT LONG-SELL PRICE: {orderHistory['avgPrice']}")
                    print(f"TRADE INFO BUY - AVG: {trade_info_buy}")
                    print(f"TRADE INFO SELL - AVG: {trade_info_sell}")
                    print(f"CURRENT GRID SIZE: {grid_size}")

                elif live_price <= (trade_info_sell[-1] - grid_size):
                    price = round((trade_info_sell[-1] - grid_size), 1)

                    print(f"TARGET SHORT-BUY PRICE: {price}")

                    precise_quantity = sell_quantity[-1]
                    orderResponseBuy = futures.UMF_place_order(c = login_key, x = coin_name, s = trade_signal_val_buy, ot = order_type, q = precise_quantity, pr = price, tif = "GTC", ps = trade_direction_val_short)
                    orderHistory = futures.UMF_query_order(c = login_key, x = coin_name, oid = orderResponseBuy["orderId"], timestamp = orderResponseBuy["updateTime"])
                    trade_info_sell.pop()
                    sell_quantity.pop()
                    last_time = entry_time_sell.pop()
                    unprecise_sell_quantity_val = unprecise_sell_quantity.pop()
                    buy_order_response = processExecuter.submit(place_long_buy_order, login_key, price, maker_brokerage, margin, leverage, coin_name, order_type, initial_balance, base_trade_value, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, long_quantity, short_quantity, pnl_counter, pnl_percent_counter, net_brokerage)
                    sell_order_response = processExecuter.submit(place_short_sell_order, login_key, price, maker_brokerage, margin, leverage, coin_name, order_type, initial_balance, base_trade_value, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, long_quantity, short_quantity, pnl_counter, pnl_percent_counter, net_brokerage)
                    buy_order_response = buy_order_response.result()
                    sell_order_response = sell_order_response.result()
                    new_unprecise_quantity = (margin * leverage) / price
                    pnl = (new_unprecise_quantity - unprecise_sell_quantity_val) * price
                    pnl_percent = (pnl / initial_balance) * 100
                    pnl_counter += pnl
                    pnl_percent_counter += pnl_percent
                    exit_margin = pnl + margin
                    amount = (margin * leverage) - pnl
                    short_quantity.value -= precise_quantity
                    time_val = datetime.datetime.now()
                    holding_time = time_val - last_time
                    brokerage = taker_brokerage * amount
                    net_brokerage.value += brokerage
                    check_balance = float(futures.UMF_balance(c = login_key, x = "USDT"))
                    buy_price = trade_info_buy.pop()
                    sell_price = trade_info_sell.pop()
                    average_price = round(((buy_price + sell_price) / 2), 2)
                    trade_info_buy.append(average_price)
                    trade_info_sell.append(average_price)
                    grid_size = round((abs(trade_info_buy[-1] - trade_info_buy[-2])), 2)
                    processExecuter.submit(live_trade_execution, coin_name, "LIVE", initial_balance, base_trade_value, leverage, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, orderResponseBuy, orderResponseBuy["type"], time_val, price, trade_direction_val_short, trade_signal_val_buy, precise_quantity, short_quantity.value, long_quantity.value, exit_margin, amount, holding_time, pnl, pnl_percent, pnl_counter, pnl_percent_counter, brokerage, net_brokerage.value, check_balance)
                    processExecuter.submit(live_generate_report, "Running", coin_name, exchange, klines_type, initial_balance, base_trade_value, leverage, quantity_multiplier, grid_size_percent, profit_percent, tick, time_val)
                    if buy_order_response:
                        processExecuter.submit(live_trade_execution, coin_name, "LIVE", initial_balance, base_trade_value, leverage, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, buy_order_response[0], buy_order_response[0]["type"], buy_order_response[1], buy_order_response[2], trade_direction_val_long, trade_signal_val_buy, buy_order_response[3], buy_order_response[4], buy_order_response[5], margin, buy_order_response[6], buy_order_response[7], buy_order_response[8], buy_order_response[9], buy_order_response[10], buy_order_response[11], buy_order_response[12], buy_order_response[13], buy_order_response[14])
                    if sell_order_response:
                        processExecuter.submit(live_trade_execution, coin_name, "LIVE", initial_balance, base_trade_value, leverage, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, sell_order_response[0], sell_order_response[0]["type"], sell_order_response[1], sell_order_response[2], trade_direction_val_short, trade_signal_val_sell, sell_order_response[3], sell_order_response[4], sell_order_response[5], margin, sell_order_response[6], sell_order_response[7], sell_order_response[8], sell_order_response[9], sell_order_response[10], sell_order_response[11], sell_order_response[12], sell_order_response[13], sell_order_response[14])
                    processExecuter.submit(live_generate_report, "Running", coin_name, exchange, klines_type, initial_balance, base_trade_value, leverage, quantity_multiplier, grid_size_percent, profit_percent, tick, time_val)

                    print(f"SQUAREDOFF AT SHORT-BUY PRICE: {orderHistory['avgPrice']}")
                    print(f"TRADE INFO BUY - AVG: {trade_info_buy}")
                    print(f"TRADE INFO SELL - AVG: {trade_info_sell}")
                    print(f"CURRENT GRID SIZE: {grid_size}")

        except Exception as err:
            exc_type, exc_obj, exc_tb = exc_info()
            check_balance = float(futures.UMF_balance(c = login_key, x = "USDT"))
            message(f'ERROR!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\nFunction: live_grid()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}')
            live_error_logs(coin_name = coin_name, initial_balance = initial_balance, base_trade_val = base_trade_value, leverage = leverage, quantity_multiplier = quantity_multiplier, grid_size_percent = grid_size_percent, profit_percent = profit_percent, exchange = exchange, klines_type = klines_type, balance = check_balance, error_msg = err)
            exit()
