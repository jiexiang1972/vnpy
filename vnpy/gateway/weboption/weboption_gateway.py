# encoding: UTF-8
"""
Author: jerry
"""

from datetime import datetime, timedelta
import time
from urllib.parse import urlencode
import urllib.request
import json
import csv
from vnpy.api.sina import sinaopapi
from threading import Thread
from copy import copy

from vnpy.trader.constant import (
    Direction,
    Exchange,
    OrderType,
    Product,
    Status,
)
from vnpy.trader.gateway import BaseGateway
from vnpy.trader.object import (
    TickData,
    OrderData,
    TradeData,
    PositionData,
    AccountData,
    ContractData,
    OrderRequest,
    CancelRequest,
    SubscribeRequest,
)

import jqdatasdk as jq

FIELDS = ["open", "high", "low", "close", "volume"]
JQEX = {"XSHG":"SSE", "XSHE":"SZSE", "CCFX":"CFFEX", "XDCE":"DCE", "XSGE":"SGE", "XZCE":"ZCE", "XINE":"INE"}
subscribeSymbols = {}  #subscribe symbols dict [symbol:time]

class WeboptionGateway(BaseGateway):
    """
    VN Trader Gateway for webopiton connection.
    """

    default_setting = {
        "usercd": "13301193374",
        "password": "xj7286",
    }

    def __init__(self, event_engine):
        """Constructor"""
        super(WeboptionGateway, self).__init__(event_engine, "WEBOPTION")
        self.thread = Thread(target=self.run)
        self.active = False

    def connect(self, setting: dict):
        """"""
        usercd = setting["usercd"]
        password = setting["password"]

        #jq.auth(usercd, password)

        self.query_contract()
        self.start()

    def subscribe(self, req: SubscribeRequest):
        """"""
        subscribeSymbols[req.symbol] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")

    def send_order(self, req: OrderRequest):
        """"""
        pass

    def cancel_order(self, req: CancelRequest):
        """"""
        pass

    def query_account(self):
        """"""
        pass

    def query_position(self):
        """"""
        pass


    def start(self):
        """"""
        self.active = True
        self.thread.start()

    def close(self):
        """尾盘发送一个tick，增加1分中，以便生成1m-K线"""
        for key in subscribeSymbols.keys():
            time.sleep(0.01)
            try:
                if key == '510050':
                    data = sinaopapi.get_etf_price(key, 'sh')
                    data["datetime"] = data["date"] + " " + data["time"]

                    data["open_interest"] = '0.0'
                else:
                    data = sinaopapi.get_op_price(key)

                tick = TickData(
                    symbol=key,
                    exchange=Exchange.SSE,
                    name=data["name"],
                    datetime=datetime.strptime(data["datetime"],'%Y-%m-%d %H:%M:%S') + timedelta(minutes=1),
                    volume=float(data["volume"]),
                    open_interest = float(data["open_interest"]),
                    last_price=float(data["last_price"]),
                    #limit_down=float(data["limit_down"]),
                    #limit_up=float(data["limit_up"]),
                    open_price=float(data["open_price"]),
                    high_price=float(data["high_price"]),
                    low_price=float(data["low_price"]),
                    pre_close=float(data["pre_close"]),
                    bid_price_1=float(data["bid_price_1"]),
                    ask_price_1=float(data["ask_price_1"]),
                    bid_volume_1=float(data["bid_volume_1"]),
                    ask_volume_1=float(data["ask_volume_1"]),
                    bid_price_2=float(data["bid_price_2"]),
                    ask_price_2=float(data["ask_price_2"]),
                    bid_volume_2=float(data["bid_volume_2"]),
                    ask_volume_2=float(data["ask_volume_2"]),
                    bid_price_3=float(data["bid_price_3"]),
                    ask_price_3=float(data["ask_price_3"]),
                    bid_volume_3=float(data["bid_volume_3"]),
                    ask_volume_3=float(data["ask_volume_3"]),
                    bid_price_4=float(data["bid_price_4"]),
                    ask_price_4=float(data["ask_price_4"]),
                    bid_volume_4=float(data["bid_volume_4"]),
                    ask_volume_4=float(data["ask_volume_4"]),
                    bid_price_5=float(data["bid_price_5"]),
                    ask_price_5=float(data["ask_price_5"]),
                    bid_volume_5=float(data["bid_volume_5"]),
                    ask_volume_5=float(data["ask_volume_5"]),
                    gateway_name=self.gateway_name,
                )

                self.on_tick(copy(tick))

                subscribeSymbols[key] = data["datetime"]
                    
            except:
                pass

        self.active = False

        if self.thread.isAlive():
            self.thread.join()
        
    def query_contract(self):
        """"""
        self.on_query_contract()

    def on_query_contract(self):
        """"""
        #print('started checking and saving data, it might take a few minutes')
        contract = ContractData(
            symbol='510050',
            exchange=Exchange.SSE,
            name='50ETF',
            product=Product.ETF,
            size=10000,
            pricetick=1 / 100,
            min_volume=1,
            gateway_name=self.gateway_name
        )
        self.on_contract(contract)
        for con in sinaopapi.get_op_contracts('510050'):
            contract = ContractData(
                symbol=con['symbol'],
                exchange=Exchange.SSE,
                name=con['name'],
                product=Product.OPTION,
                size=10000,
                pricetick=1 / 10000,
                min_volume=1,
                gateway_name=self.gateway_name,
                option_strike = float(con['option_strike']),
                option_underlying = con['option_underlying'],     # vt_symbol of underlying contract
                option_type = con['option_type'],
                option_expiry = datetime.strptime(con["option_expiry"], "%Y-%m-%d")
            )
            self.on_contract(contract)
            print(f'"{contract.symbol}.SSE": {{"symbol": "{contract.symbol}", "exchange": "SSE","gateway_name": "WEBOPTION"}},')
        self.write_log("合约查询成功")

    def run(self):
        """get market data"""
        while self.active:
            for key in subscribeSymbols.keys():
                time.sleep(0.01)
                try:
                    if key == '510050':
                        data = sinaopapi.get_etf_price(key, 'sh')
                        data["datetime"] = data["date"] + " " + data["time"]
                        data["open_interest"] = '0.0'
                    else:
                        data = sinaopapi.get_op_price(key)
                    if data["datetime"] != subscribeSymbols[key]:
                        tick = TickData(
                            symbol=key,
                            exchange=Exchange.SSE,
                            name=data["name"],
                            datetime=datetime.strptime(data["datetime"],'%Y-%m-%d %H:%M:%S'),
                            volume=float(data["volume"]),
                            open_interest = float(data["open_interest"]),
                            last_price=float(data["last_price"]),
                            #limit_down=float(data["limit_down"]),
                            #limit_up=float(data["limit_up"]),
                            open_price=float(data["open_price"]),
                            high_price=float(data["high_price"]),
                            low_price=float(data["low_price"]),
                            pre_close=float(data["pre_close"]),
                            bid_price_1=float(data["bid_price_1"]),
                            ask_price_1=float(data["ask_price_1"]),
                            bid_volume_1=float(data["bid_volume_1"]),
                            ask_volume_1=float(data["ask_volume_1"]),
                            bid_price_2=float(data["bid_price_2"]),
                            ask_price_2=float(data["ask_price_2"]),
                            bid_volume_2=float(data["bid_volume_2"]),
                            ask_volume_2=float(data["ask_volume_2"]),
                            bid_price_3=float(data["bid_price_3"]),
                            ask_price_3=float(data["ask_price_3"]),
                            bid_volume_3=float(data["bid_volume_3"]),
                            ask_volume_3=float(data["ask_volume_3"]),
                            bid_price_4=float(data["bid_price_4"]),
                            ask_price_4=float(data["ask_price_4"]),
                            bid_volume_4=float(data["bid_volume_4"]),
                            ask_volume_4=float(data["ask_volume_4"]),
                            bid_price_5=float(data["bid_price_5"]),
                            ask_price_5=float(data["ask_price_5"]),
                            bid_volume_5=float(data["bid_volume_5"]),
                            ask_volume_5=float(data["ask_volume_5"]),
                            gateway_name=self.gateway_name,
                        )

                        self.on_tick(copy(tick))

                        subscribeSymbols[key] = data["datetime"]
                        
                except:
                    pass
