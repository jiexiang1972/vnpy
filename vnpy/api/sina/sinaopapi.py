"""
Author: shifulin
Email: shifulin666@qq.com
"""
# python3
from requests import get
import time
from vnpy.trader.constant import Exchange, OptionType


def get_op_dates():
    url = "http://stock.finance.sina.com.cn/futures/api/openapi.php/StockOptionService.getStockName"
    dates = get(url).json()['result']['data']['contractMonth']
    return [''.join(i.split('-')) for i in dates][1:]


def get_op_expire_day(date):
    url = "http://stock.finance.sina.com.cn/futures/api/openapi.php/StockOptionService.getRemainderDay?date={date}01"
    data = get(url.format(date=date)).json()['result']['data']
    return data['expireDay'], int(data['remainderDays'])


def get_op_codes(date, symbol):
    url_up = "http://hq.sinajs.cn/list=OP_UP_{symbol}".format(symbol=symbol) + str(date)[-4:]
    url_down = "http://hq.sinajs.cn/list=OP_DOWN_{symbol}".format(symbol=symbol) + str(date)[-4:]
    data_up = str(get(url_up).content).replace('"', ',').split(',')
    codes_up = [i[7:] for i in data_up if i.startswith('CON_OP_')]
    data_down = str(get(url_down).content).replace('"', ',').split(',')
    codes_down = [i[7:] for i in data_down if i.startswith('CON_OP_')]
    return codes_up, codes_down


def get_op_price(code):
    url = "http://hq.sinajs.cn/list=CON_OP_{code}".format(code=code)
    data = get(url).content.decode('gbk')
    data = data[data.find('"') + 1: data.rfind('"')].split(',')
    fields = ['ask_volume', 'ask_price', 'last_price', 'bid_price', 'bid_volume', 'open_interest', '涨幅', 
              'option_strike', 'pre_close', 'open_price', 'limit_up',
              'limit_down', 'bid_price_5', 'bid_volume_5', 'bid_price_4', 'bid_volume_4', 'bid_price_3', 'bid_volume_3', 'bid_price_2',
              'bid_volume_2', 'bid_price_1', 'bid_volume_1', 'ask_price_1', 'ask_volume_1', 'ask_price_2', 'ask_volume_2', 'ask_price_3',
              'ask_volume_3', 'ask_price_4', 'ask_volume_4', 'ask_price_5', 'ask_volume_5', 'datetime', '主力合约标识', '状态码',
              '标的证券类型', 'option_underlying', 'name', '振幅', 'high_price', 'low_price', 'volume', '成交额', 'M', 'last_price_M']
    result = dict(zip(fields, data))
    return result


def get_etf_price(symbol, market):
    url = f"http://hq.sinajs.cn/list={market}{symbol}"
    data = get(url).content.decode('gbk')
    data = data[data.find('"') + 1: data.rfind('"')].split(',')
    fields = ['name', 'open_price', 'pre_close', 'last_price', 'high_price', 'low_price', 'ask_price', 'bid_price',
              'volume', '成交金额', 'ask_volume_1', 'ask_price_1', 'ask_volume_2', 'ask_price_2', 'ask_volume_3', 
              'ask_price_3', 'ask_volume_4', 'ask_price_4',
              'ask_price_5', 'ask_volume_5', 'bid_volume_1', 'bid_price_1', 'bid_volume_2', 'bid_price_2', 'bid_volume_3', 
              'bid_price_3', 'bid_volume_4', 'bid_price_4',
              'bid_volume_5', 'bid_price_5', 'date', 'time']
    return dict(zip(fields, data))


def get_op_greek_alphabet(code):
    url = "http://hq.sinajs.cn/list=CON_SO_{code}".format(code=code)
    data = get(url).content.decode('gbk')
    data = data[data.find('"') + 1: data.rfind('"')].split(',')
    fields = ['name', 'volume', 'Delta', 'Gamma', 'Theta', 'Vega', 'IV', 'high_price', 'low_price', 'code',
              'option_strike', 'last_price', 'theory_price']
    return dict(zip(fields, [data[0]] + data[4:]))

def get_op_contracts(underlying):
    dates = get_op_dates()
    print('期权合约月份：{}'.format(dates))
    con = []
    for date in dates:
        expire_day, remainder_days = get_op_expire_day(date)
        ups, downs = get_op_codes(date, underlying)
        for up in ups:
            time.sleep(0.05)
            data = get_op_price(up)
            if data['M'] == 'M':
                d = {}
                d['symbol'] = up
                d['name'] = data['name']
                d['option_expiry'] = expire_day
                d['option_strike'] = data['option_strike']
                d['option_type'] = OptionType.CALL
                d['option_underlying'] = underlying
                con.append(d)
        for down in downs:
            time.sleep(0.05)
            data = get_op_price(down)
            if data['M'] == 'M':
                d = {}
                d['symbol'] = down
                d['name'] = data['name']
                d['option_expiry'] = expire_day
                d['option_strike'] = data['option_strike']
                d['option_type'] = OptionType.PUT
                d['option_underlying'] = underlying
                con.append(d)
    return con        

    
if __name__ == '__main__':
    print(get_op_contracts('510050'))

    dates = get_op_dates()
    print('期权合约月份：{}'.format(dates))
    for date in dates:
        print('期权月份{}：到期日{} 剩余天数{}'.format(date, *get_op_expire_day(date)))
    for date in dates:
        print('期权月份{}\n\t看涨期权代码：{}\n\t看跌期权代码：{}'.format(date, *get_op_codes(date, '510050')))
    #for index, i in enumerate(get_op_price('10001778')):
    print('期权10001778', get_op_price('10001778'))
    #for index, i in enumerate(get_etf_price('510050', 'sh')):
    print('50ETF', get_etf_price('510050', 'sh'))
    #for index, i in enumerate(get_op_greek_alphabet('10001778')):
    print('期权10001778', get_op_greek_alphabet('10001778'))