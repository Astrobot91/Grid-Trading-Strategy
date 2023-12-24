import db
import datetime
from telegram import message

coll_trade_history = db.connect_coll("AlgoTrading", "Trade_History")
coll_error_logs = db.connect_coll("AlgoTrading", "Error_Logs")
coll_reports = db.connect_coll("AlgoTrading", "Reports")

def live_error_logs(coin_name, exchange, klines_type, initial_balance, base_trade_val, leverage, quantity_multiplier, grid_size_percent, profit_percent, balance, error_msg):

    coll_error_logs.insert_one(
        {
            "StrategyName" : "GRID",
            "TradingType" : "LIVE",
            "CurrencyPair" : coin_name,
            "Exchange" : exchange,
            "ExchangeType" : klines_type,
            "InitialBalance" : initial_balance,
            "BaseTradeValue" : base_trade_val,
            "Leverage" : leverage,
            "QtyMultiplier" : quantity_multiplier,
            "GridSizePercent" : grid_size_percent,
            "ProfitSetPercent" : profit_percent,
            "DateTime" : datetime.datetime.now(),
            "Balance" : balance,
            "ErrorMsg" : error_msg
        }
    )  

def live_trade_execution(coin_name, trading_type, initial_balance, base_trade_val, leverage, quantity_multiplier, grid_size_percent, profit_percent, exchange, klines_type, order_response, order_type, time_val, price, trade_direction_val, trade_signal_val, bitcoins, short_quantity, long_quantity, margin, amount, holding_time, pnl, pnl_percent, npnl, npnl_percent, brokerage, net_brokerage, balance):

    live_trade_data = {
        "StrategyName" : "GRID",
        "TradingType" : trading_type,
        "CurrencyPair" : coin_name,
        "Exchange" : exchange,
        "ExchangeType" : klines_type,
        "InitialBalance" : initial_balance,
        "BaseTradeValue" : base_trade_val,
        "Leverage" : leverage,
        "QtyMultiplier" : quantity_multiplier,
        "GridSizePercent" : grid_size_percent,
        "ProfitSetPercent" : profit_percent,
        "OrderResponse" : order_response,
        "OrderType" : order_type,
        "DateTime" : time_val,
        "Price" : price,
        "TradeDirection" : trade_direction_val,
        "TradeSignal" : trade_signal_val,
        "Quantity" : bitcoins,
        "ShortQty" : short_quantity,
        "LongQty" : long_quantity,
        "Margin" : margin,
        "Amount" : amount,
        "HoldingTime" :str(holding_time),
        "PNL" : round(pnl, 2),
        "PNLPercent" : round(pnl_percent, 2),
        "NPNL" : round(npnl, 2),
        "NPNLPercent" : round(npnl_percent, 2),
        "Brokerage" : brokerage,
        "NetBrokerage" : net_brokerage,
        "Balance" : round(balance, 2)
        }

    coll_trade_history.insert_one(live_trade_data)    

    message(f'NEW TRADE!\n\nProject: GRID Strategy - Alpha\nFolder: GRID OPT\nFile: livegrid.py\n\nOrder : \n{live_trade_data}')  

def live_generate_report(status, coin_name, exchange, klines_type, balance_store, base_trade_val, leverage, quantity_multiplier, grid_size_percent, profit_percent, tick, tock):

    noOfTrades_pipeline = [
        {
            "$match" : {
                "StrategyName": "GRID",
                "TradingType": "LIVE",
                "CurrencyPair": coin_name,
                "Exchange": exchange,
                "ExchangeType": klines_type,
                "InitialBalance": balance_store,
                "BaseTradeValue": base_trade_val,
                "Leverage": leverage,
                "QtyMultiplier": quantity_multiplier,
                "GridSizePercent": grid_size_percent,
                "ProfitSetPercent": profit_percent,
                "PNL" : {"$ne" : 0},
            }
        },
        {
            "$count" : "Total Trades"
        }
    ]

    win_trades_pipeline = [
        {
            "$match" : {
                "StrategyName": "GRID",
                "TradingType": "LIVE",
                "CurrencyPair": coin_name,
                "Exchange": exchange,
                "ExchangeType": klines_type,
                "InitialBalance": balance_store,
                "BaseTradeValue": base_trade_val,
                "Leverage": leverage,
                "QtyMultiplier": quantity_multiplier,
                "GridSizePercent": grid_size_percent,
                "ProfitSetPercent": profit_percent,
                "PNL" : {"$gt" : 0},
            }
        },
        {
            "$count" : "Win Trades",
        }
    ]

    lose_trades_pipeline = [
        {
            "$match" : {
                "StrategyName": "GRID",
                "TradingType": "LIVE",
                "CurrencyPair": coin_name,
                "Exchange": exchange,
                "ExchangeType": klines_type,
                "InitialBalance": balance_store,
                "BaseTradeValue": base_trade_val,
                "Leverage": leverage,
                "QtyMultiplier": quantity_multiplier,
                "GridSizePercent": grid_size_percent,
                "ProfitSetPercent": profit_percent,
                "PNL" : {"$lt" : 0},
            }
        },
        {
            "$count" : "Lose Trades",
        }
    ]

    profit_pipeline = [
        {
            "$match" : {
                "StrategyName": "GRID",
                "TradingType": "LIVE",
                "CurrencyPair": coin_name,
                "Exchange": exchange,
                "ExchangeType": klines_type,
                "InitialBalance": balance_store,
                "BaseTradeValue": base_trade_val,
                "Leverage": leverage,
                "QtyMultiplier": quantity_multiplier,
                "GridSizePercent": grid_size_percent,
                "ProfitSetPercent": profit_percent,
            }
        },
        {"$sort" : {"DateTime" : -1}},
        {"$limit" : 1},
        {"$project" : {"_id" : 0, "NPNL" : 1, "NPNLPercent" : 1, "Balance" : 1}}
    ]

    margin_in_trade_pipeline = [
        { 
            "$match" : { 
                "StrategyName": "GRID",
                "TradingType": "LIVE",
                "CurrencyPair": coin_name,
                "Exchange": exchange,
                "ExchangeType": klines_type,
                "InitialBalance": balance_store,
                "BaseTradeValue": base_trade_val,
                "Leverage": leverage,
                "QtyMultiplier": quantity_multiplier,
                "GridSizePercent": grid_size_percent,
                "ProfitSetPercent": profit_percent,
            }
        },
        { "$sort" : { "DateTime" : -1 } },
        { "$limit" : 1 },
        { "$project" : { "_id" : 0, "ShortQty" : 1, "LongQty" : 1, "Price" : 1 } },
        { "$addFields" : { "TotalQty" : { "$add" : ["$ShortQty", "$LongQty"] } } },
        { "$project" : { "Margin in Trade Currently" : { "$multiply" : ["$TotalQty", "$Price"] } } }
    ]           

    noOfTrades_val = list(coll_trade_history.aggregate(noOfTrades_pipeline))
    winTrade_val = list(coll_trade_history.aggregate(win_trades_pipeline))
    loseTrade_val = list(coll_trade_history.aggregate(lose_trades_pipeline))
    profit_val = list(coll_trade_history.aggregate(profit_pipeline))
    margin_in_trade_val = list(coll_trade_history.aggregate(margin_in_trade_pipeline))

    def number_of_trades():
        if not noOfTrades_val:
            trades_number = 0
        else:
            trades_number = noOfTrades_val[0]["Total Trades"] 
        return trades_number

    def number_of_win_trades():
        if  not winTrade_val:
            win_trades_number = 0
        else:
            win_trades_number = winTrade_val[0]["Win Trades"] 
        return win_trades_number
    
    def number_of_lose_trades():
        if not loseTrade_val:
            lose_trades_number = 0
        else:
            lose_trades_number =  loseTrade_val[0]["Lose Trades"]
        return lose_trades_number
    
    def profit():
        if not profit_val:
            return 0
        else:
            return profit_val[0]["NPNL"]

    def profit_percentage():
        if not profit_val:
            return 0
        else:
            return profit_val[0]["NPNLPercent"]
    
    def balance():
        if not profit_val:
            return 0
        else:
            return profit_val[0]["Balance"]

    def margin():
        if not margin_in_trade_val:
            return 0    
        else:
            return margin_in_trade_val[0]["Margin in Trade Currently"]

    t = number_of_trades()
    w = number_of_win_trades()
    l = number_of_lose_trades()

    def hit_rate():
        try: 
            return w / t
        except ZeroDivisionError:
            return 0

    filter = {
        "StrategyName": "GRID",
        "TradingType": "LIVE",
        "CurrencyPair": coin_name,
        "Exchange": exchange,
        "ExchangeType": klines_type,
        "InitialBalance": balance_store,
        "BaseTradeValue": base_trade_val,
        "Leverage": leverage,
        "QtyMultiplier": quantity_multiplier,
        "GridSizePercent": grid_size_percent,
        "ProfitSetPercent": profit_percent,
    }

    update = {
        "$set" : {
            "StrategyName": "GRID",
            "TradingType": "LIVE",
            "Status" : status,
            "CurrencyPair": coin_name,
            "Exchange": exchange,
            "ExchangeType": klines_type,
            "InitialBalance": balance_store,
            "BaseTradeValue": base_trade_val,
            "Leverage": leverage,
            "QtyMultiplier": quantity_multiplier,
            "GridSizePercent": grid_size_percent,
            "ProfitSetPercent": profit_percent,
            "No. of Trades" : t,
            "Win Trades" : w,
            "Lose Trades" : l,
            "Breakeven Trades" : (t - (w + l)),
            "HitRate" : hit_rate(),
            "Profit" : profit(),
            "ProfitPercent" : profit_percentage(),
            "Margin in Trade" : margin() / leverage,
            "Balance" : balance(),
            "Runtime" : str(tock - tick)
        }
    }

    updater = coll_reports.update_many(filter, update)
    
    if updater.matched_count == 0:
        coll_reports.insert_one(
            {
            "StrategyName": "GRID",
            "TradingType": "LIVE",
            "Status" : status,
            "CurrencyPair": coin_name,
            "Exchange": exchange,
            "ExchangeType": klines_type,
            "InitialBalance": balance_store,
            "BaseTradeValue": base_trade_val,
            "Leverage": leverage,
            "QtyMultiplier": quantity_multiplier,
            "GridSizePercent": grid_size_percent,
            "ProfitSetPercent": profit_percent,
            "No of Trades" : t,
            "Win Trades" : w,
            "Lose Trades" : l,
            "Breakeven Trades" : (t - (w + l)),
            "HitRate" : hit_rate(),
            "Profit" : profit(),
            "Profit%" : profit_percentage(),
            "Margin in Trade" : margin() / leverage,
            "Balance" : balance(),
            "Runtime" : str(tock - tick)
            }
        )
    else:
        coll_reports.update_many(filter, update)

 