from ctypes import *
from PyQt5.QtWidgets import *
from TSMsater_32 import TScanAPI
import sys
import threading
from threading import Lock, Thread

canfd = TScanAPI.TLIBCANFD()

obj1 = c_size_t(0)


def OnPreRxCANEvent(ACAN):
    print("回调事件发送接受can.FIdentifier = ", ACAN.contents.FIdentifier)


OnRxCANEvent = TScanAPI.OnTx_RxFUNC_CAN(OnPreRxCANEvent)
size = c_int(16)


class FirstDemo(QWidget):
    def __init__(self):
        super(FirstDemo, self).__init__()
        self.initUI()

    def initUI(self):
        self.resize(300, 200)
        self.setWindowTitle("TSMasterAPIDemo")
        layout = QVBoxLayout()

        self.btn_ConnectAPI = QPushButton("连接硬件")
        self.btn_ConnectAPI.clicked.connect(self.ConnectAPI)

        self.btn_SendMessage = QPushButton("发送报文")
        self.btn_SendMessage.clicked.connect(self.SendMessage)

        self.btn_DisConnectAPI = QPushButton("断开连接")
        self.btn_DisConnectAPI.clicked.connect(self.DisConnectAPI)

        self.btn_event_Rxcan = QPushButton("Rx事件")
        self.btn_event_Rxcan.clicked.connect(self.OnCANRxEvent)

        layout.addWidget(self.btn_ConnectAPI)
        layout.addWidget(self.btn_SendMessage)
        layout.addWidget(self.btn_DisConnectAPI)
        layout.addWidget(self.btn_event_Rxcan)

        self.setLayout(layout)

    def ConnectAPI(self):
        TScanAPI.initialize_lib_tsmaster(True, False)
        connectAPI = TScanAPI.tsapp_connect('', obj1)
        connectAPI = TScanAPI.tsapp_register_event_can(obj1, OnRxCANEvent)
        # CAN波特率
        # connectAPI = TScanAPI.tsapp_configure_baudrate_can(obj1, 0, c_double(500), 1)
        # connectAPI = TScanAPI.tsapp_configure_baudrate_can(obj1, 1, c_double(500), 1)

        # CANFD波特率
        connectAPI = TScanAPI.tsapp_configure_baudrate_canfd(obj1, 0, c_double(500), c_double(2000),
                                                             TScanAPI.TLIBCANFDControllerType.lfdtISOCAN.value,
                                                             TScanAPI.TLIBCANFDControllerMode.lfdmNormal.value,
                                                             TScanAPI.A120.ENABLEA120.value)
        connectAPI = TScanAPI.tsapp_configure_baudrate_canfd(obj1, 1, c_double(500), c_double(2000),
                                                             TScanAPI.TLIBCANFDControllerType.lfdtISOCAN.value,
                                                             TScanAPI.TLIBCANFDControllerMode.lfdmNormal.value,
                                                             TScanAPI.A120.ENABLEA120.value)
        print(connectAPI)
        if (connectAPI == 0):
            print("连接成功")
            # 多线程异步接收
            # 需要循环运行TScanAPI.tsapp_receive_can_msgs，在API中注释的代码，可直接运行
            # t_sing = threading.Thread(target=TScanAPI.tsapp_receive_can_msgs, args=(obj1,message1,size,0,1))
            # t_sing.start()
        else:
            print('连接失败')

    def SendMessage(self):
        msg = TScanAPI.TLIBCAN()
        msg.FIdxChn = 0
        msg.FIdentifier = 0x100
        msg.FProperties = 5
        msg.FDLC = 8
        FData = [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17]
        for i in range(len(FData)):
            msg.FData[i] = FData[i]
        ret = TScanAPI.tsapp_transmit_can_async(obj1, msg)
        # print(ret)
        msg1 = TScanAPI.TLIBCANFD()
        msg1.FIdxChn = 0
        msg1.FIdentifier = 0x101
        msg1.FProperties = 5
        msg1.FFDProperties = 1
        msg1.FDLC = 11
        FData1 = [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x20]
        for i in range(len(FData1)):
            msg1.FData[i] = FData1[i]

        ret = TScanAPI.tsapp_transmit_canfd_async(obj1, msg1)

        # print(ret)

    def OnCANRxEvent(self):

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
                print("{:#x}".format(list[i].FIdentifier))

        ret = TScanAPI.tsapp_receive_canfd_msgs(obj1, list1, size, chn, txrx)
        for i in range(16):
            if list1[i].FIdentifier != 0x00:
                print("{:#x}".format(list1[i].FIdentifier))

    def DisConnectAPI(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = FirstDemo()
    main.show()
    sys.exit(app.exec_())
