#!/usr/bin/env python
# @Time   :2021/11/3 12:24
# @Author :SEVEN
# @File   :TSMater.py
# @Comment:use func with TSMaster.dll
# ------------------------------------------------

from ctypes import *
import sys
import threading
from threading import Lock,Thread
from time import sleep
# dll = WinDLL(r".\libTSCAN.dll")
dll = WinDLL(r".\libTSCAN.dll")

class TLIBCAN(Structure):
    _pack_ = 1
    _fields_ = [("FIdxChn", c_uint8),
                ("FProperties", c_uint8),
                ("FDLC", c_uint8),  # TLIBApplicationChannelType
                ("FReserved", c_uint8),  # TLIBBusToolDeviceType
                ("FIdentifier", c_int32),
                ("FTimeUs", c_uint64),
                ("FData", c_uint8 * 8),
                ]
    def __init__(self,FIdxChn:c_uint8,FIdentifier:c_int32,FDLC:c_uint8,FData):
        self.FIdxChn = FIdxChn
        self.FIdentifier =FIdentifier
        self.FProperties = 0
        self.FDLC = FDLC
        for i in range(len(FData)):
            self.FData[i] = FData[i]


class TLIBCANFD(Structure):
    _pack_ = 1
    _fields_ = [("FIdxChn", c_ubyte),
                ("FProperties", c_ubyte),
                ("FDLC", c_ubyte),  # TLIBApplicationChannelType
                ("FFDProperties", c_ubyte),  # TLIBBusToolDeviceType
                ("FIdentifier", c_int),
                ("FTimeUs", c_ulonglong),
                ("FData", c_ubyte * 64),
                ]
    def __init__(self,FIdxChn:c_uint8,FIdentifier:c_int32,FDLC:c_uint8,FData):
        self.FIdxChn = c_ubyte(FIdxChn)
        self.FIdentifier =c_int(FIdentifier)
        self.FProperties = 0
        self.FFProperties = 3
        self.FDLC = c_ubyte(FDLC)
        for i in range(len(FData)):
            self.FData[i] = c_uint8(FData[i])

class TLIBLIN(Structure):
    _pack_ = 1
    _fields_ = [("FIdxChn", c_ubyte),
                ("FErrCode", c_ubyte),
                ("FProperties", c_ubyte),#0:RX 1:TX
                ("FDLC", c_uint8),  # TLIBApplicationChannelType

                ("FIdentifier", c_ubyte),
                ("FChecksum", c_ubyte),
                ("FStatus", c_ubyte),
                ("FTimeUs", c_ulonglong),
                ("FData", c_uint8 * 8),
                ]

    def __init__(self, FIdxChn: c_uint8, FProperties:c_uint8,FIdentifier: c_int32, FDLC: c_uint8, FData):
        self.FIdxChn = FIdxChn
        self.FProperties = FProperties
        self.FIdentifier = FIdentifier
        self.FProperties = 1
        self.FDLC = FDLC
        for i in range(len(FData)):
            self.FData[i] = c_uint8(FData[i])
PCAN = POINTER(TLIBCAN)
OnTx_RxFUNC_CAN = WINFUNCTYPE(None, PCAN)

PLIN = POINTER(TLIBLIN)
OnTx_RxFUNC_LIN = WINFUNCTYPE(None, PLIN)

PCANFD = POINTER(TLIBCANFD)
OnTx_RxFUNC_CANFD = WINFUNCTYPE(None, PCANFD)

# 初始化函数（是否使能fifo,是否激活极速模式）
def initialize_lib_tsmaster(AEnableFIFO:c_bool,AEnableTurbe:c_bool):
    dll.initialize_lib_tscan(True, False)

# 连接硬件(ADeviceSerial != null:连接指定的设备 为null为任意硬件 )
def tsapp_connect(ADeviceSerial:str,AHandle:c_size_t):
    r = dll.tscan_connect(ADeviceSerial, byref(AHandle))
    return r

# 断开指定硬件连接
def tsapp_disconnect_AHandle(AHandle:c_size_t):
    r = dll.tscan_disconnect(AHandle)
    return r

# 断开所有硬件连接
def tsapp_disconnect():
    r = dll.tscan_disconnect_all_devices()
    return r

# 设置can参数
def tsapp_configure_baudrate_can(ADeviceHandle:c_size_t,AChnIdx:c_double,ARateKbps:c_double,A120:c_uint):
    r = dll.tscan_config_can_by_baudrate(ADeviceHandle,AChnIdx,ARateKbps,A120)
    return r

# 设置canfd参数
def tsapp_configure_baudrate_canfd(ADeviceHandle:c_size_t,AChnIdx:c_int32,ARateKbps:c_double,ADataKbps:c_double,AControllerType,AControllerMode,A120:c_uint):
    r = dll.tscan_config_canfd_by_baudrate(ADeviceHandle,AChnIdx,ARateKbps,ADataKbps,AControllerType,AControllerMode,A120)
    return r

# 设置lin参数
def tsapp_configure_baudrate_lin(ADeviceHandle:c_size_t,AChnIdx:c_int32,ARateKbps:c_double):
    r = dll.tslin_config_baudrate(ADeviceHandle,AChnIdx,ARateKbps)
    return r

# lin设置主节点
def tsapp_set_node_funtiontype(ADeviceHandle:c_size_t,AChnIdx:c_int32,AFunctionType:c_ubyte):
    r = dll.tslin_set_node_funtiontype(ADeviceHandle,AChnIdx,AFunctionType)
    return r

# 下载ldf
def tsapp_apply_download_new_ldf(ADeviceHandle:c_size_t,AChnIdx:c_int32):
    r = dll.tslin_apply_download_new_ldf(ADeviceHandle,AChnIdx)
    return r

# 异步发送can报文
def tsapp_transmit_can_async(AHandle:c_size_t,Msg:TLIBCAN):
    r = dll.tscan_transmit_can_async(AHandle,addressof(Msg))
    return r

# 同步发送can报文
def tsapp_transmit_can_sync(AHandle:c_size_t,Msg:TLIBCAN,ATimeoutMS:c_int32):
    r = dll.tscan_transmit_can_sync(AHandle,addressof(Msg),ATimeoutMS)
    return r

# 异步发送canfd报文
def tsapp_transmit_canfd_async(AHandle:c_size_t,Msg:TLIBCANFD):
    r = dll.tscan_transmit_canfd_async(AHandle,addressof(Msg))
    return r

# 同步发送canfd报文
def tsapp_transmit_canfd_sync(AHandle:c_size_t,Msg:TLIBCANFD,ATimeoutMS:c_int32):
    r = dll.tscan_transmit_canfd_async(AHandle,addressof(Msg),ATimeoutMS)
    return r

# 异步发送lin报文
def tsapp_transmit_lin_async(AHandle:c_size_t,Msg:TLIBLIN):
    r = dll.tslin_transmit_lin_async(AHandle,addressof(Msg))
    return r

# 同步发送lin报文
def tsapp_transmit_lin_sync(AHandle:c_size_t,Msg:TLIBLIN,ATimeoutMS:c_int32):
    r = dll.tslin_transmit_lin_sync(AHandle,addressof(Msg),ATimeoutMS)
    return r

# 异步发送lin报文
def tsapp_transmit_lin_async(AHandle:c_size_t,Msg:TLIBLIN):
    r = dll.tslin_transmit_lin_async(AHandle,addressof(Msg))
    return r

# 同步发送fastlin报文
def tsapp_transmit_fastlin_sync(AHandle:c_size_t,Msg:TLIBLIN,ATimeoutMS:c_int32):
    r = dll.tslin_transmit_fastlin_sync(AHandle,addressof(Msg),ATimeoutMS)
    return r

# can报文接收
def tsapp_receive_can_msgs(AHandle:c_size_t,ACANBuffers:TLIBCAN,ACANBufferSize:c_uint,AChn:c_ubyte,ARxTx:c_ubyte):
    r = dll.tsfifo_receive_can_msgs(AHandle, byref(ACANBuffers), byref(ACANBufferSize), AChn, ARxTx)
    return r
    # FIdentifier = 0x100
    # while(True):
    #     r = dll.tsfifo_receive_can_msgs(AHandle,addressof(ACANBuffers),addressof(ACANBufferSize),AChn,ARxTx)
    #
    #     if(ACANBuffers.FIdentifier != FIdentifier):
    #         FIdentifier =ACANBuffers.FIdentifier
    #         print(ACANBuffers.FIdentifier)
    #     # sleep(0.1)


# canfd报文接收
def tsapp_receive_canfd_msgs(AHandle:c_size_t,ACANBuffers:TLIBCANFD,ACANBufferSize:c_uint,AChn:c_ubyte,ARxTx:c_ubyte):
    r = dll.tsfifo_receive_canfd_msgs(AHandle,addressof(ACANBuffers),ACANBufferSize,AChn,ARxTx)
    return r

# lin报文接收
def tsapp_receive_lin_msgs(AHandle:c_size_t,ACANBuffers:TLIBLIN,ACANBufferSize:c_uint,AChn:c_ubyte,ARxTx:c_ubyte):
    r = dll.tsfifo_receive_lin_msgs(AHandle,addressof(ACANBuffers),addressof(ACANBufferSize),ARxTx)
    return r

# fastlin报文接收
def tsapp_receive_fastlin_msgs(AHandle:c_size_t,ACANBuffers:TLIBLIN,ACANBufferSize:c_uint,AChn:c_ubyte,ARxTx:c_ubyte):
    r = dll.tsfifo_receive_fastlin_msgs(AHandle,addressof(ACANBuffers),addressof(ACANBufferSize),AChn,ARxTx)
    return r

# 注册can发送接收事件
def tsapp_register_event_can(AHandle:c_size_t,ACallback):
    r = dll.tscan_register_event_can(AHandle,ACallback)
    return r
# 注销can发送接收事件
def tsapp_unregister_event_can(AHandle:c_size_t,ACallback):
    r =  dll.tscan_unregister_event_can(AHandle,ACallback)
    return r
# 注册lin发送接收事件
def tsapp_register_event_lin(AHandle:c_size_t,ACallback):
    r = dll.tslin_register_event_lin(AHandle,ACallback)
    return r
# 注销lin发送接收事件
def tsapp_unregister_event_lin(AHandle:c_size_t,ACallback):
    r = dll.tslin_unregister_event_lin(AHandle,ACallback)
    return r
# 注册lin发送接收事件
def tsapp_register_event_fastlin(AHandle:c_size_t,ACallback):
    r = dll.tscan_register_event_fastlin(AHandle,ACallback)
    return r
# 注销lin发送接收事件
def tsapp_unregister_event_fastlin(AHandle:c_size_t,ACallback):
    r = dll.tscan_unregister_event_fastlin(AHandle,ACallback)
    return r

# 注册回放通道
def tsapp_Register_Replay_MapChannel(AHandle:c_size_t,APPchannel:c_int32,HWchannel:c_int32):
    r =dll.Replay_RegisterReplayMapChannel(AHandle,APPchannel,HWchannel)
    return r

# 注销回放通道
def tsapp_unRegister_Replay_MapChannel(AHandle:c_size_t):
    dll.Replay_ClearReplayMapChannel(AHandle)

# 回放blf
def tsapp_start_repaly_blf(AHandle:c_size_t,ABlfFilePath:str,ATriggerByHardware:c_int,AStartUs:c_ulonglong,AEndUs:c_ulonglong):
    r = dll.Replay_Start_Blf(AHandle,ABlfFilePath,c_int(ATriggerByHardware),AStartUs,AEndUs)
    return r

# 停止回放
def tsapp_stop_repaly_blf(AHandle:c_size_t):
    r = dll.Replay_Stop(AHandle)
    return r