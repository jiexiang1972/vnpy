# encoding: UTF-8

import multiprocessing
from time import sleep
from datetime import datetime, time

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp
from vnpy.gateway.weboption import WeboptionGateway
from vnpy.app.data_recorder import DataRecorderApp


#----------------------------------------------------------------------
def processErrorEvent(event):
    """
    处理错误事件
    错误信息在每次登陆后，会将当日所有已产生的均推送一遍，所以不适合写入日志
    """
    error = event.dict_['data']
    print(u'错误代码：%s，错误信息：%s' %(error.errorID, error.errorMsg))

#----------------------------------------------------------------------
def runChildProcess():
    """子进程运行函数"""
    print('-'*20)

    # 创建日志引擎
    #le = LogEngine()
    #le.setLogLevel(le.LEVEL_INFO)
    #le.addConsoleHandler()
    print('启动行情记录运行子进程')
    
    event_engine = EventEngine()
    #ee = EventEngine2()
    print('事件引擎创建成功')
    
    main_engine = MainEngine(event_engine)
    
    main_engine.add_gateway(WeboptionGateway)
    main_engine.add_app(DataRecorderApp)

    print('主引擎创建成功')

    #ee.register(EVENT_LOG, le.processLogEvent)
    #ee.register(EVENT_ERROR, processErrorEvent)
    #le.info(u'注册日志事件监听')

    _setting = {
        "usercd": "13301193374",
        "password": "xj7286",
    }
    main_engine.connect(_setting, 'WEBOPTION')
    print('连接web option接口')

    while True:
        sleep(1)

#----------------------------------------------------------------------
def runParentProcess():
    """父进程运行函数"""
    # 创建日志引擎
    #le = LogEngine()
    #le.setLogLevel(le.LEVEL_INFO)
    #le.addConsoleHandler()
    print(u'启动行情记录守护父进程')
    
    DAY_START = time(9, 15)         # 日盘启动和停止时间
    DAY_END = time(15, 5)
    NIGHT_START = time(23, 59)      # 夜盘启动和停止时间
    NIGHT_END = time(00, 00)
    
    p = None        # 子进程句柄

    while True:
        currentTime = datetime.now().time()
        recording = False

        # 判断当前处于的时间段
        if ((currentTime >= DAY_START and currentTime <= DAY_END) 
            #or (currentTime >= NIGHT_START)
            #or (currentTime <= NIGHT_END)
           ):
            recording = True
            
        # 过滤周末时间段：周六全天，周五夜盘，周日日盘
        if ((datetime.today().weekday() == 6) or 
            (datetime.today().weekday() == 5 and currentTime > NIGHT_END) or 
            (datetime.today().weekday() == 0 and currentTime < DAY_START)):
            recording = False

        # 记录时间则需要启动子进程
        if recording and p is None:
            print('启动子进程')
            p = multiprocessing.Process(target=runChildProcess)
            p.start()
            print('子进程启动成功')

        # 非记录时间则退出子进程
        if not recording and p is not None:
            print(u'关闭子进程')
            p.terminate()
            p.join()
            p = None
            print(u'子进程关闭成功')

        sleep(5)


if __name__ == '__main__':
    #runChildProcess()
    runParentProcess()