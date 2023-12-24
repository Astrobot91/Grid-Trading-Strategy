from livegrid import live_grid

# GRID PARAMETERS
exchange = "BINANCE"
klines_type = "FUTURES"

base_trade_val = 1          # Set Base Trade Value
leverage = 125              # Set Leverage
quantity_multiplier = 1     # Increase the quantity
grid_size_percent = 0.01    # Set grid Size Percent
profit_percent = 0.01       # Set Profit Percent
quantity_multiplier = 1     # Set Quantity Multiplier
order_type = "MARKET"        # Set Order Type LIMIT / MARKET

symbol = "BTCUSDT"

api_key = "akBzzyjHe3B3ewbXO5IoCsofl9sxxuJZzCf9vRScn9e16piyG0TPtYW4SL0443ES"
secret_key = "OH0xpkSfXcXdTg0SzSaswnn4NlMqpBIpgYqDQV27RZoayIUafNoUjyCcFYig5LE7"

live_grid(public_key = api_key, secret_key = secret_key, coin_name = symbol, exchange = exchange, klines_type = klines_type, base_trade_value = base_trade_val, leverage = leverage, profit_percent = profit_percent, quantity_multiplier = quantity_multiplier, grid_size_percent = grid_size_percent, order_type = order_type)

