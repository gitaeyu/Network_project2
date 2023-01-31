# GUI 채팅 클라이언트
import sys
from socket import *
from threading import *
import json
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMessageBox

from PyQt5.QtCore import *
from PyQt5 import uic, QtGui
form_class = uic.loadUiType('./untitled.ui')[0]
form_class2 = uic.loadUiType('./create_room.ui')[0]

class Popup(QDialog,form_class2):

    def __init__(self,parent):
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        self.create_rm_btn.clicked.connect(self.create_room)


    def create_room(self):
        name = self.room_naming_lineEdit.text()
        gamekind = self.game_kind_cb.currentText()
        numpeople = self.num_people_cb.currentText()
        roominfo = [name,gamekind,numpeople]
        tempdata = json.dumps(roominfo)
        message = tempdata + "000008"
        self.parent.client_socket.send(message.encode())
        self.close()

class Main(QMainWindow, form_class):
    client_socket = None

    def __init__(self,ip,port):
        super().__init__()
        self.setupUi(self)
        self.initialize_socket(ip,port)
        self.stackedWidget.setCurrentIndex(1)
        self.listen_thread()
        self.login_btn.clicked.connect(self.login_signal_send)
        self.message_send_btn.clicked.connect(self.send_chat)
        self.client_create_rm_btn.clicked.connect(self.create_rm_client)
        # self.follow_up_invite_btn.clicked.connect(self.invite_user)
        self.idlist=[]
        self.gameidlist=[]

    def create_rm_client(self):
        createpop = Popup(self)
        createpop.exec_()
    def closeEvent(self, e):
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            e.accept()
            self.client_socket.send("!@$#@#Socke@$close".encode())
            self.threadSignal = False
            print('Window closed')
        else:
            e.ignore()
    def invite_user(self):
        selected_user = self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
        message = (selected_user + "753357").encode()
        self.client_socket.send(message)
    def login_signal_send(self):
        self.id = self.login_id_lineEdit.text()
        password = self.login_pw_lineEdit.text()
        sendlist = [self.id,password]
        tempdata = json.dumps(sendlist)
        send_message = tempdata + "654321"
        self.client_socket.send(send_message.encode())
        print('success')
        self.stackedWidget.setCurrentIndex(4)

    def initialize_socket(self,ip,port):
        '''
        TCP socket을 생성하고 server와 연결
        '''
        self.client_socket = socket(AF_INET,SOCK_STREAM)
        remote_ip = ip
        remote_port = port
        self.client_socket.connect((remote_ip,remote_port))

    def send_chat(self):
        '''
        message를 전송하는 버튼 콜백 함수
        '''
        senders_name = self.id
        data =self.game_lineEdit.text()
        message = (senders_name +': '+data+'123456').encode('utf-8')
        self.client_socket.send(message)
        self.game_lineEdit.clear()
        return 'break'

    def listen_thread(self):
        '''
        데이터 수신 Thread를 생성하고 시작한다.
        '''
        self.threadSignal=True
        self.t=Thread(target=self.signal_check,args=(self.client_socket,))
        self.t.start()

    def signal_check(self,so):
        while self.threadSignal:
            buf = so.recv(1024)
            print(buf)
            signal = buf.decode()
            print(signal)
            if signal[-6:] == "123456":
                self.textBrowser.append(signal[:-6] + '\n')
            elif signal[-6:]  == "985674" :
                self.idlist = json.loads(signal[:-6])
                print(self.idlist)
                self.tableWidget.setRowCount(len(self.idlist))
                self.tableWidget.setColumnCount(1)
                for i in range(len(self.idlist)):
                    self.tableWidget.setItem(i, 0, QTableWidgetItem(str(self.idlist[i])))
            elif signal[-6:]  == "000009" :
                self.roomlist = json.loads(signal[:-6])
                print(self.roomlist)
                self.tableWidget_4.setRowCount(len(self.roomlist))
                self.tableWidget_4.setColumnCount(len(self.roomlist[0]))
                for i in range(len(self.roomlist)):
                    for j in range(len(self.roomlist[i])):
                        # i번째 줄의 j번째 칸에 데이터를 넣어줌
                        self.tableWidget_4.setItem(i, j, QTableWidgetItem(str(self.roomlist[i][j])))
            # elif signal[-6:] =='846574' :
            #     self.gameidlist.append(signal[:-6])
            #     print(self.gameidlist)
            #     self.tableWidget_2.setRowCount(len(self.gameidlist))
            #     self.tableWidget_2.setColumnCount(1)
            #     for i in range(len(self.gameidlist)):
            #         self.tableWidget_2.setItem(i, 0, QTableWidgetItem(str(self.gameidlist[i])))


#!@!@#@!
if __name__ == "__main__":
    ip, port = "10.10.21.103", 9048


    app = QApplication(sys.argv)
    mainWindow = Main(ip,port)
    mainWindow.setFixedWidth(1024)
    mainWindow.setFixedHeight(1000)
    mainWindow.show()
    app.exec_()