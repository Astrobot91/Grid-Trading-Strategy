import time
import json
import websocket
from queue import Queue
import threading

live_price_queue = Queue()

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

thread0 = threading.Thread(target = fetch_live_price, args = ("BTCUSDT",))
thread0.start()

while True:
    live_price = live_price_queue.get()
    print(live_price)

