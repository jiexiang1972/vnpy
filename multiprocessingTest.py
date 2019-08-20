from multiprocessing import Process, Value
import os, time, random

# 写数据进程执行的代码:
def write(q):
    print('Process to write: %s' % q.value)
    q.value=8
    print('Process to write: %s' % q.value)
    while  q.value != 10:
        time.sleep(5)
    print('Process to write: %s' % q.value)

def runParentProcess():
    q = Value("i", 5)
    pw = Process(target=write, args=(q,))

    # 启动子进程pw，写入:
    pw.start()
    # 等待pw结束:
    time.sleep(30)

    q.value = 10
    pw.join()
    # pr进程里是死循环，无法等待其结束，只能强行终止:
    #pr.terminate()


if __name__=='__main__':
    runParentProcess()
