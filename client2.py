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
        id = self.parent.id
        roominfo = [name,gamekind,numpeople,id]
        tempdata = json.dumps(roominfo)
        message = tempdata + "000008"
        self.parent.stackedWidget.setCurrentIndex(6)
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
        self.join_game_btn.clicked.connect(self.join_fu_game)
        self.show_main6.clicked.connect(self.exit_game_room)
    def exit_game_room(self):
        roomnumber = self.follow_up_rm_number.text()
        user_1id = self.user_1_label.text()
        user_2id = self.user_2_label.text()
        user_3id = self.user_3_label.text()
        user_4id = self.user_4_label.text()

        exit_room_info = [roomnumber,user_1id,user_2id,user_3id,user_4id,self.id]
        tempdata = json.dumps(exit_room_info)
        message = tempdata + "000013"
        self.stackedWidget.setCurrentIndex(4)
        self.client_socket.send(message.encode())

    def create_rm_client(self):
        createpop = Popup(self)
        createpop.exec_()
    def closeEvent(self, e):
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            e.accept()
            self.exit_game_room()
            self.client_socket.send("!@$#@#Socke@$close".encode())
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

        self.t=Thread(target=self.signal_check,args=(self.client_socket,))
        self.t.daemon = True
        self.t.start()

    def signal_check(self,so):
        while True:
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
                if self.roomlist != [] :
                    self.tableWidget_4.setRowCount(len(self.roomlist))
                    self.tableWidget_4.setColumnCount(len(self.roomlist[0]))
                    for i in range(len(self.roomlist)):
                        for j in range(len(self.roomlist[i])):
                            # i번째 줄의 j번째 칸에 데이터를 넣어줌
                            self.tableWidget_4.setItem(i, j, QTableWidgetItem(str(self.roomlist[i][j])))
            elif signal[-6:]  == "000010" :
                self.rminfolist = json.loads(signal[:-6])
                self.follow_up_game_room_refresh()


    def join_fu_game(self):
        selected_rm_number = self.tableWidget_4.item(self.tableWidget_4.currentRow(), 0).text()
        selected_people = self.tableWidget_4.item(self.tableWidget_4.currentRow(), 2).text()
        max_people = self.tableWidget_4.item(self.tableWidget_4.currentRow(), 3).text()
        if selected_people == max_people :
            QMessageBox.critical(self, "인원 꽉참", "방을 만들거나 다른 방에 접속해주세요")
            return
        select_rm_info = [selected_rm_number,selected_people,self.id]
        tempdata = json.dumps(select_rm_info)
        message = tempdata + "000011"
        self.stackedWidget.setCurrentIndex(6)

        self.client_socket.send(message.encode())


    def follow_up_game_room_refresh(self):
        self.follow_up_rm_number.setText(str(self.rminfolist[0]))
        self.user_1_label.setText(self.rminfolist[1])
        self.user_2_label.setText(self.rminfolist[2])
        self.user_3_label.setText(self.rminfolist[3])
        self.user_4_label.setText(self.rminfolist[4])



#!@!@#@!
if __name__ == "__main__":
    ip, port = "127.0.0.1", 9048


    app = QApplication(sys.argv)
    mainWindow = Main(ip,port)
    mainWindow.setFixedWidth(1024)
    mainWindow.setFixedHeight(1000)
    mainWindow.show()
    app.exec_()