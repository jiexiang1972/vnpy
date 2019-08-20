# encoding: UTF-8

import multiprocessing
from time import sleep
from datetime import datetime, time
from logging import INFO 

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.setting import SETTINGS
from vnpy.trader.ui import MainWindow, create_qapp
from vnpy.gateway.weboption import WeboptionGateway
from vnpy.app.data_recorder import DataRecorderApp, EVENT_RECORDER_LOG


#----------------------------------------------------------------------
SETTINGS["log.active"] = True 
SETTINGS["log.level"] = INFO 
SETTINGS["log.console"] = True 


#----------------------------------------------------------------------
def runChildProcess(running_flag):
    """子进程运行函数"""
    SETTINGS["log.file"] = True
    
    print('-'*20)

    print('启动行情记录运行子进程')
    
    event_engine = EventEngine()
    print('事件引擎创建成功')
    
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(WeboptionGateway)
    main_engine.add_app(DataRecorderApp)

    main_engine.write_log("主引擎创建成功")

    log_engine = main_engine.get_engine("log") 
    event_engine.register(EVENT_RECORDER_LOG, log_engine.process_log_event) 
    main_engine.write_log("注册日志事件监听") 


    _setting = {
        "usercd": "13301193374",
        "password": "xj7286",
    }

    main_engine.connect(_setting, 'WEBOPTION')
    main_engine.write_log("连接web option接口")

    while running_flag .value:
        sleep(1)

    #sleep(15)
    main_engine.write_log("子进程结束\n")
    main_engine.get_gateway('WEBOPTION').close()  #先关闭gateway，记录最后K线
    main_engine.close()

#----------------------------------------------------------------------
def runParentProcess():
    """父进程运行函数"""
    print('启动行情记录守护父进程')
    
    DAY_START = time(9, 25)         # 日盘启动和停止时间
    DAY_END = time(16, 50)
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
        if ((datetime.today().weekday() == 5) or (datetime.today().weekday() == 6)
           # or (datetime.today().weekday() == 5 and currentTime > NIGHT_END)  
           # or (datetime.today().weekday() == 0 and currentTime < DAY_START)
           ):
            recording = False

        # 记录时间则需要启动子进程
        if recording and p is None:
            print('启动子进程')
            running_flag = multiprocessing.Value("i", 1)
            p = multiprocessing.Process(target=runChildProcess, args=(running_flag, ))
            p.start()
            print('子进程启动成功')

        # 非记录时间则退出子进程
        if not recording and p is not None:
            print('关闭子进程')
            running_flag.value = not running_flag.value
            #p.terminate()
            p.join() #(60)
            p = None
            print('子进程关闭成功')

        sleep(5)


if __name__ == '__main__':
    #runChildProcess(False)
    runParentProcess()