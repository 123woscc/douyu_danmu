# coding:utf-8
__author__ = 'CC'
__date__='2017/7/19'

import socket
import time
from struct import pack
import json
import re
from collections import deque
from threading import Thread

#弹幕放置容器
d=deque()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname('openbarrage.douyutv.com')
port = 12601

#连接服务器
client.connect((host, port))

#向服务器发送数据
def send_data(data):
    s = pack('i', 9 + len(data)) * 2
    s += pack('i',689)
    s += data.encode() + b'\x00'
    client.sendall(s)

#登录斗鱼服务器
def login(rid):
    data = 'type@=loginreq/username@=rieuse/password@=douyu/roomid@={}/\0'.format(rid)
    send_data(data)


#发送获取弹幕请求
def get_danmu(rid):
    data = 'type@=joingroup/rid@={}/gid@=-9999/\0'.format(rid)
    send_data(data)


#获取服务器返回的数据
def get_data():
    while True:
        try:
            data=client.recv(1024)
            parse_data(data)
        except Exception as e:
            pass

#格式化并保存弹幕
def parse_data(data):
    try:
        data1 = re.findall(b'(type@=.*?)\x00', data)[0]
        data2 = data1.replace(b'@=', b'":"').replace(b'/', b'","')
        data3 = data2.decode('utf8', 'ignore')[:-2]
        data4 = json.loads('{"' + data3 + '}')

        #过滤type为chatmsg的信息
        if data4['type'] == 'chatmsg':
            msg = '[{}]:{}'.format(data4['nn'], data4['txt'])
            d.append(msg)
    except Exception as e:
        pass


#心跳包
def keep_alive():
    while True:
        send_data('type@=keeplive/tick@={}/'.format(int(time.time())))
        time.sleep(10)



def run(rid):
    login(rid)
    get_danmu(rid)

    #开启多线程
    t1=Thread(target=get_data)
    t2=Thread(target=keep_alive)

    #设置守护线程
    t1.setDaemon(True)
    t2.setDaemon(True)


    t1.start()
    t2.start()

    while True:
        if len(d) > 0:
            print(d.popleft())







if __name__ == '__main__':
    room_id=input('斗鱼房间ID:')
    # room_id=271934
    run(room_id)



