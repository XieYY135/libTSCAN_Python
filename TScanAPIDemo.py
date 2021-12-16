from ctypes import *
from PyQt5.QtWidgets import *
import TScanAPI
import sys
import threading
from threading import Lock, Thread
import time

canfd = TScanAPI.TLIBCANFD()

obj1 = c_size_t(0)


def OnPreRxCANEvent(ACAN):
    print("回调事件发送接受can.FIdentifier ={:#x}".format(ACAN.contents.FIdentifier))


OnRxCANEvent = TScanAPI.OnTx_RxFUNC_CAN(OnPreRxCANEvent)
size = c_int(16)


def ConnectAPI():
    TScanAPI.initialize_lib_tsmaster(True, False)
    connectAPI = TScanAPI.tsapp_connect("", obj1)
    if (connectAPI == 0):
        print("连接成功")
    connectAPI = TScanAPI.tsapp_register_event_can(obj1, OnRxCANEvent)
    # CAN波特率
    # connectAPI = TScanAPI.tsapp_configure_baudrate_can(obj1, 0, c_double(500), 1)
    # connectAPI = TScanAPI.tsapp_configure_baudrate_can(obj1, 1, c_double(500), 1)

    # # CANFD波特率
    connectAPI = TScanAPI.tsapp_configure_baudrate_canfd(obj1, 0, c_double(500), c_double(2000),
                                                         TScanAPI.TLIBCANFDControllerType.lfdtISOCAN.value,
                                                         TScanAPI.TLIBCANFDControllerMode.lfdmNormal.value,
                                                         TScanAPI.A120.ENABLEA120.value)

    connectAPI = TScanAPI.tsapp_configure_baudrate_canfd(obj1, 1, c_double(500), c_double(2000),
                                                         TScanAPI.TLIBCANFDControllerType.lfdtISOCAN.value,
                                                         TScanAPI.TLIBCANFDControllerMode.lfdmNormal.value,
                                                         TScanAPI.A120.ENABLEA120.value)
    if (connectAPI == 0):
        print("波特率设置成功")

        # 多线程异步接收
        # 需要循环运行TScanAPI.tsapp_receive_can_msgs，在API中注释的代码，可直接运行
        # t_sing = threading.Thread(target=TScanAPI.tsapp_receive_can_msgs, args=(obj1,message1,size,0,1))
        # t_sing.start()
    else:
        print('连接失败')


def SendMessage():
    msg = TScanAPI.TLIBCAN()
    msg.FIdxChn = 0
    msg.FIdentifier = 0x100
    msg.FProperties = 5
    msg.FDLC = 8
    FData = [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17]
    for i in range(len(FData)):
        msg.FData[i] = FData[i]
    ms = c_float(100)
    # ret = TScanAPI.tsapp_transmit_can_async(obj1, msg)
    ret = TScanAPI.tscan_add_cyclic_msg_can(obj1, msg, ms)
    if (ret == 0):
        print('can报文发送成功')
    else:
        print('can报文发送失败')
    msg1 = TScanAPI.TLIBCANFD()
    msg1.FIdxChn = 0
    msg1.FIdentifier = 0x101
    msg1.FProperties = 5
    msg1.FFDProperties = 1
    msg1.FDLC = 11
    FData1 = [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x20]
    for i in range(len(FData1)):
        msg1.FData[i] = FData1[i]

    # ret = TScanAPI.tsapp_transmit_canfd_async(obj1, msg1)
    ret = TScanAPI.tscan_add_cyclic_msg_canfd(obj1, msg1,ms)
    if (ret == 0):
        print('canfd报文发送成功')
    else:
        print('canfd报文发送失败')


def OnCANRxEvent():
    list = []
    for i in range(16):
        item = TScanAPI.TLIBCAN()
        list.append(item)
    message1 = TScanAPI.TLIBCAN()

    list1 = []
    for i in range(16):
        item = TScanAPI.TLIBCANFD()
        list1.append(item)

    chn = c_ubyte(1)

    # print(len(list))
    txrx = c_ubyte(1)
    # print(message1)
    ret = TScanAPI.tsapp_receive_can_msgs(obj1, list, size, chn, txrx)

    for i in range(16):
        if list[i].FIdentifier != 0x00:
            print("can接收到1通道报文id= {:#x}".format(list[i].FIdentifier))

    ret = TScanAPI.tsapp_receive_canfd_msgs(obj1, list1, size, chn, txrx)
    for i in range(16):
        if list1[i].FIdentifier != 0x00:
            print("canfd接收到1通道报文id={:#x}".format(list1[i].FIdentifier))


def DisConnectAPI():
    pass


if __name__ == '__main__':
    i = 5
    ConnectAPI()
    SendMessage()
    time.sleep(10)
    OnCANRxEvent()
    time.sleep(1)
