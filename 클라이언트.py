import sys
from socket import *
from threading import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic, QtGui

from os import environ

form_class = uic.loadUiType("abc.ui")[0]

class Main(QMainWindow, form_class):
    Client_socket = None

    def __init__(self, ip, port):
        super().__init__()
        self.setupUi(self)
        self.initialize_socket(ip, port)
        self.listen_thread()
        self.send_btn.clicked.connect(self.send_chat)
        self.room_add_btn.clicked.connect(self.add_chat_room)
        self.chat_room_list.clicked.connect(self.chat_view)

        self.test_btn.clicked.connect(self.chat_view)
        self.test_btn2.clicked.connect(self.chat_list_view)


    def add_chat_room(self):
        chat_name = self.chat_room_add_edit.text()
        self.client_socket.send((chat_name+"003").encode('utf-8'))      #채팅 룸 추가 코드 003
        self.chat_room_add_edit.clear()

    def chat_list_view(self):
        self.chat_room_list.clear()
        self.client_socket.send("002".encode('utf-8'))

    def chat_view(self):
        room_text = self.chat_room_list.selectedItems()
        for item in room_text:
            room_name = item.text()
        self.client_socket.send((room_name + "004").encode('utf-8'))    # 클라이언트의 선택된 채팅 룸이름을 알려주기 위함.
        self.text_view.clear()
        self.client_socket.send((room_name + "001").encode('utf-8'))

    def initialize_socket(self,ip,port):
        self.client_socket = socket(AF_INET,SOCK_STREAM)
        remote_ip = ip
        remote_port = port
        self.client_socket.connect((remote_ip,remote_port))


    def send_chat(self):
        senders_name = self.name_edit.text()
        data = self.text_edit.text()
        message = (senders_name+': '+data).encode('utf-8')
        self.text_view.addItem(message.decode('utf-8')+'\n')
        self.client_socket.send(message)

        self.text_edit.clear()
        self.text_view.scrollToBottom()
        return 'break'

    def listen_thread(self):
        t = Thread(target=self.receive_message, args=(self.client_socket,))
        t.start()


    def receive_message(self,so):
        while True:
            buf = so.recv(512)
            text = buf.decode('utf-8')
            if not buf: #연결 종료 됨
                break
            if text[-3:] == '000':                      # 메시지 송수신
                self.text_view.addItem(text[:-3])
            elif text[-3:] == '001':                    # 채팅 불러오기
                self.text_view.scrollToBottom()
                self.text_view.addItem(text[:-3])
                self.text_view.scrollToBottom()
                self.text_view.addItem("")
            elif text[-3:] == '002':                    # 채팅방 목록 불러오기
                self.chat_room_list.addItem(text[:-3])
            # elif text[-3:] == '004':                    # 선택 채팅한 채팅방 채팅 불러오기


        so.close()

if __name__ == "__main__":
    ip = '127.0.0.1'
    port = 55000

    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCREEN_FACTOR"] = "1"

    app = QApplication(sys.argv)
    mainWindow = Main(ip, port)
    mainWindow.show()
    app.exec_()