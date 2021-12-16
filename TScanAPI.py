#!/usr/bin/env python
# @Time   :2021/11/24 12:24
# @Author :SEVEN
# @File   :TScanAPI.py
# @Comment:使用python64 将需要添加libTSCAN.dll libTSH.dll (x64);
# 使用python32 将需要添加libTSCAN.dll libTSH.dll libLog.dll binlog.dll(x32)
# ------------------------------------------------
from enum import Enum
from ctypes import *
import copy

dll = WinDLL(r".\libTSCAN.dll")


class CHANNEL_INDEX(Enum):
    (
        CHN1, CHN2, CHN3, CHN4, CHN5, CHN6, CHN7, CHN8, CHN9, CHN10, CHN11, CHN12, CHN13, CHN14, CHN15, CHN16, CHN17,
        CHN18, CHN19, CHN20, CHN21, CHN22, CHN23, CHN24, CHN25, CHN26, CHN27, CHN28, CHN29, CHN30, CHN31, CHN32) = (
        c_int(0), c_int(1), c_int(2), c_int(3), c_int(4), c_int(5), c_int(6), c_int(7), c_int(8), c_int(9), c_int(10),
        c_int(11), c_int(12), c_int(13), c_int(14), c_int(15), c_int(16), c_int(17), c_int(18), c_int(19), c_int(20),
        c_int(21), c_int(22), c_int(23), c_int(24), c_int(25), c_int(26), c_int(27), c_int(28), c_int(29),
        c_int(30),
        c_int(31)
    )


class READ_TX_RX_DEF(Enum):
    ONLY_RX_MESSAGES = c_int(0)
    TX_RX_MESSAGES = c_int(1)


class LIN_PROTOCOL(Enum):
    LIN_PROTOCOL_13 = c_int(0)
    LIN_PROTOCOL_20 = c_int(1)
    LIN_PROTOCOL_21 = c_int(2)
    LIN_PROTOCOL_J2602 = c_int(3)


class T_LIN_NODE_FUNCTION(Enum):
    T_MASTER_NODE = c_int(0)
    T_SLAVE_NODE = c_int(1)
    T_MONITOR_NODE = c_int(2)


class TLIBCANFDControllerType(Enum):
    lfdtCAN = c_int(0)
    lfdtISOCAN = c_int(1)
    lfdtNonISOCAN = c_int(2)


class TLIBCANFDControllerMode(Enum):
    lfdmNormal = c_int(0)
    lfdmACKOff = c_int(1)
    lfdmRestricted = c_int(2)


class A120(Enum):
    DEABLEA120 = c_int(0)
    ENABLEA120 = c_int(1)


class TLIBCAN(Structure):
    _pack_ = 1
    _fields_ = [("FIdxChn", c_uint8),
                ("FProperties", c_uint8),  # 定义can数据类型  1:标准数据帧 3:标准远程帧 5：扩展数据帧 7：扩展远程帧
                ("FDLC", c_uint8),
                ("FReserved", c_uint8),
                ("FIdentifier", c_int32),
                ("FTimeUs", c_uint64),
                ("FData", c_uint8 * 8),
                ]


class TLIBCANFD(Structure):
    _pack_ = 1
    _fields_ = [("FIdxChn", c_ubyte),
                ("FProperties", c_ubyte),  # 定义canfd数据类型  1:FD标准帧 5:FD扩展帧
                ("FDLC", c_ubyte),
                ("FFDProperties", c_ubyte),  # 0:普通can数据帧 1：canfd数据帧
                ("FIdentifier", c_int),
                ("FTimeUs", c_ulonglong),
                ("FData", c_ubyte * 64),
                ]


class TLIBLIN(Structure):
    _pack_ = 1
    _fields_ = [("FIdxChn", c_ubyte),
                ("FErrCode", c_ubyte),
                ("FProperties", c_ubyte),
                ("FDLC", c_uint8),
                ("FIdentifier", c_ubyte),
                ("FChecksum", c_ubyte),
                ("FStatus", c_ubyte),
                ("FTimeUs", c_ulonglong),
                ("FData", c_uint8 * 8),
                ]


PCAN = POINTER(TLIBCAN)
OnTx_RxFUNC_CAN = WINFUNCTYPE(None, PCAN)

PLIN = POINTER(TLIBLIN)
OnTx_RxFUNC_LIN = WINFUNCTYPE(None, PLIN)

PCANFD = POINTER(TLIBCANFD)
OnTx_RxFUNC_CANFD = WINFUNCTYPE(None, PCANFD)


# 初始化函数（是否使能fifo,是否激活极速模式）
def initialize_lib_tsmaster(AEnableFIFO: c_bool, AEnableTurbe: c_bool):
    dll.initialize_lib_tscan(AEnableFIFO, AEnableTurbe)


# 连接硬件(ADeviceSerial为null为任意硬件 )
def tsapp_connect(ADeviceSerial: str, AHandle: c_size_t):
    r = dll.tscan_connect(ADeviceSerial, byref(AHandle))
    return r


# 断开指定硬件连接
def tsapp_disconnect_AHandle(AHandle: c_size_t):
    r = dll.tscan_disconnect(AHandle)
    return r


# 断开所有硬件连接
def tsapp_disconnect():
    r = dll.tscan_disconnect_all_devices()
    return r


# 设置can参数
def tsapp_configure_baudrate_can(ADeviceHandle: c_size_t, AChnIdx: CHANNEL_INDEX, ARateKbps: c_double, A120: A120):
    r = dll.tscan_config_can_by_baudrate(ADeviceHandle, AChnIdx, ARateKbps, A120)
    return r


# 设置canfd参数
def tsapp_configure_baudrate_canfd(ADeviceHandle: c_size_t, AChnIdx: CHANNEL_INDEX, ARateKbps: c_double,
                                   ADataKbps: c_double,
                                   AControllerType: TLIBCANFDControllerType, AControllerMode: TLIBCANFDControllerMode,
                                   A120: A120):
    r = dll.tscan_config_canfd_by_baudrate(ADeviceHandle, AChnIdx, ARateKbps, ADataKbps, AControllerType,
                                           AControllerMode, A120)
    return r


# 设置lin参数
def tsapp_configure_baudrate_lin(ADeviceHandle: c_size_t, AChnIdx: CHANNEL_INDEX, ARateKbps: c_double):
    r = dll.tslin_config_baudrate(ADeviceHandle, AChnIdx, ARateKbps)
    return r


# lin设置主节点
def tsapp_set_node_funtiontype(ADeviceHandle: c_size_t, AChnIdx: CHANNEL_INDEX, AFunctionType: T_LIN_NODE_FUNCTION):
    r = dll.tslin_set_node_funtiontype(ADeviceHandle, AChnIdx, AFunctionType)
    return r


# 下载ldf
def tsapp_apply_download_new_ldf(ADeviceHandle: c_size_t, AChnIdx: CHANNEL_INDEX):
    r = dll.tslin_apply_download_new_ldf(ADeviceHandle, AChnIdx)
    return r


# 异步发送can报文
def tsapp_transmit_can_async(AHandle: c_size_t, Msg: TLIBCAN):
    r = dll.tscan_transmit_can_async(AHandle, byref(Msg))
    return r


# 同步发送can报文
def tsapp_transmit_can_sync(AHandle: c_size_t, Msg: TLIBCAN, ATimeoutMS: c_int32):
    r = dll.tscan_transmit_can_sync(AHandle, byref(Msg), ATimeoutMS)
    return r


# 异步发送canfd报文
def tsapp_transmit_canfd_async(AHandle: c_size_t, Msg: TLIBCANFD):
    r = dll.tscan_transmit_canfd_async(AHandle, byref(Msg))
    return r


# 同步发送canfd报文
def tsapp_transmit_canfd_sync(AHandle: c_size_t, Msg: TLIBCANFD, ATimeoutMS: c_int32):
    r = dll.tscan_transmit_canfd_async(AHandle, byref(Msg), ATimeoutMS)
    return r

# 循环发送canfd报文
def tscan_add_cyclic_msg_canfd(AHandle: c_size_t, Msg: TLIBCANFD, ATimeoutMS: c_float):
    r = dll.tscan_add_cyclic_msg_canfd(AHandle, byref(Msg), ATimeoutMS)
    return r

# 删除循环发送canfd报文
def tscan_delete_cyclic_msg_canfd(AHandle: c_size_t, Msg: TLIBCANFD):
    r = dll.tscan_delete_cyclic_msg_canfd(AHandle, byref(Msg))
    return r

# 周期发送canfd报文
def tscan_add_cyclic_msg_can(AHandle: c_size_t, Msg: TLIBCAN, ATimeoutMS: c_float):
    r = dll.tscan_add_cyclic_msg_can(AHandle, byref(Msg), ATimeoutMS)
    return r

# 删除循环发送can报文
def tscan_delete_cyclic_msg_can(AHandle: c_size_t, Msg: TLIBCAN):
    r = dll.tscan_delete_cyclic_msg_can(AHandle, byref(Msg))
    return r

# 异步发送lin报文
def tsapp_transmit_lin_async(AHandle: c_size_t, Msg: TLIBLIN):
    r = dll.tslin_transmit_lin_async(AHandle, byref(Msg))
    return r


# 同步发送lin报文
def tsapp_transmit_lin_sync(AHandle: c_size_t, Msg: TLIBLIN, ATimeoutMS: c_int32):
    r = dll.tslin_transmit_lin_sync(AHandle, byref(Msg), ATimeoutMS)
    return r


# can报文接收
def tsapp_receive_can_msgs(AHandle: c_size_t, ACANBuffers: TLIBCAN, ACANBufferSize: c_uint, AChn: CHANNEL_INDEX,
                           ARxTx: c_ubyte):
    temp = copy.copy(ACANBufferSize)
    data = POINTER(TLIBCAN * len(ACANBuffers))((TLIBCAN * len(ACANBuffers))(*ACANBuffers))
    r = dll.tsfifo_receive_can_msgs(AHandle, data, byref(temp), AChn, ARxTx)
    for i in range(len(data.contents)):
        ACANBuffers[i] = data.contents[i]
    return r


# canfd报文接收
def tsapp_receive_canfd_msgs(AHandle: c_size_t, ACANFDBuffers: TLIBCANFD, ACANFDBufferSize: c_uint, AChn: CHANNEL_INDEX,
                             ARxTx: c_ubyte):
    temp = copy.copy(ACANFDBufferSize)
    data = POINTER(TLIBCANFD * len(ACANFDBuffers))((TLIBCANFD * len(ACANFDBuffers))(*ACANFDBuffers))
    r = dll.tsfifo_receive_canfd_msgs(AHandle, data, byref(temp), AChn, ARxTx)
    for i in range(len(data.contents)):
        ACANFDBuffers[i] = data.contents[i]
    return r


# lin报文接收
def tsapp_receive_lin_msgs(AHandle: c_size_t, ALINBuffers: TLIBLIN, ALINBufferSize: c_uint, AChn: CHANNEL_INDEX,
                           ARxTx: c_ubyte):
    temp = copy.copy(ALINBufferSize)
    data = POINTER(TLIBLIN * len(ALINBuffers))((TLIBLIN * len(ALINBuffers))(*ALINBuffers))
    r = dll.tsfifo_receive_lin_msgs(AHandle, data, byref(temp), AChn, ARxTx)
    for i in range(len(data.contents)):
        ALINBuffers[i] = data.contents[i]
    return r


# 注册can发送接收事件
def tsapp_register_event_can(AHandle: c_size_t, ACallback):
    r = dll.tscan_register_event_can(AHandle, ACallback)
    return r


# 注销can发送接收事件
def tsapp_unregister_event_can(AHandle: c_size_t, ACallback):
    r = dll.tscan_unregister_event_can(AHandle, ACallback)
    return r


# 注册lin发送接收事件
def tsapp_register_event_lin(AHandle: c_size_t, ACallback):
    r = dll.tslin_register_event_lin(AHandle, ACallback)
    return r


# 注销lin发送接收事件
def tsapp_unregister_event_lin(AHandle: c_size_t, ACallback):
    r = dll.tslin_unregister_event_lin(AHandle, ACallback)
    return r



# 回放blf
def tsapp_start_repaly_blf(AHandle: c_size_t, ABlfFilePath: str, ATriggerByHardware: c_int, AStartUs: c_ulonglong,
                           AEndUs: c_ulonglong):
    r = dll.Replay_Start_Blf(AHandle, ABlfFilePath, ATriggerByHardware, AStartUs, AEndUs)
    return r


# 停止回放
def tsapp_stop_repaly_blf(AHandle: c_size_t):
    r = dll.Replay_Stop(AHandle)
    return r
