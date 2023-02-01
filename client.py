# GUI 채팅 클라이언트
import sys
from socket import *
from threading import *
import json
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMessageBox

from PyQt5 import uic, QtGui
form_class = uic.loadUiType('./untitled.ui')[0]
form_class2 = uic.loadUiType('./create_room.ui')[0]
form_class3 = uic.loadUiType('./invite.ui')[0]


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
        self.follow_up_invite_btn.clicked.connect(self.invite_client)
        self.idlist=[]
        self.gameidlist=[]
        self.join_game_btn.clicked.connect(self.join_fu_game)
        self.show_main6.clicked.connect(self.exit_game_room)
        self.invite_accept_btn.clicked.connect(self.invite_accept2)
        self.invite_reject_btn.clicked.connect(self.invite_reject)
        self.follow_up_start_btn.clicked.connect(self.game_start)
        self.invite_message_label.hide()
        self.invite_accept_btn.hide()
        self.invite_reject_btn.hide()
        self.follow_up_send_lineEdit.setText("")
        self.follow_up_send_btn.clicked.connect(self.word_send)

    def word_send(self):

        prev_word = self.follow_up_word_lbl.text()
        word = self.follow_up_send_lineEdit.text()
        if self.client_id_lbl.text() == self.user_1_label.text() :
            self.order = 1
        elif self.client_id_lbl.text() == self.user_2_label.text() :
            self.order = 2
        elif self.client_id_lbl.text() == self.user_3_label.text() :
            self.order = 3
        elif self.client_id_lbl.text() == self.user_4_label.text() :
            self.order =4
        turn = int(self.Turn_lbl.text())
        current_people = int(self.current_people_lbl.text())
        self.game_order = turn % current_people
        if self.game_order == 0 :
            self.game_order = current_people
        if self.order != self.game_order :
            QMessageBox.critical(self, "차례 아님", "턴을 기다려주세요")
            return
        elif prev_word[-1] != word[0] :
            rm_number = self.follow_up_rm_number.text()
            game_info = ["FAIL", rm_number, turn, current_people,word]
            tempdata = json.dumps(game_info)
            message = tempdata + "828282"  # 게임 관련 식별 코드
            self.client_socket.send(message.encode())
        else :
            rm_number = self.follow_up_rm_number.text()
            game_info = ["CHECK", rm_number, turn, current_people,word]
            tempdata = json.dumps(game_info)
            message = tempdata + "828282"  # 게임 관련 식별 코드
            self.client_socket.send(message.encode())



    def invite_reject(self):
        self.invite_message_label.hide()
        self.invite_accept_btn.hide()
        self.invite_reject_btn.hide()
    def invite_accept2(self):
        print("수락")
        print(self.invited_room_info)
        invited_rm_number = self.invited_room_info[0][0]
        invited_rm_people = self.invited_room_info[0][2]
        invited_rm_max_people = self.invited_room_info[0][3]
        if invited_rm_people == invited_rm_max_people:
            QMessageBox.critical(self, "인원 꽉참", "방을 만들거나 다른 방에 접속해주세요")
            return
        select_rm_info = [invited_rm_number, invited_rm_people, self.id]
        tempdata = json.dumps(select_rm_info)
        message = tempdata + "000011"
        self.stackedWidget.setCurrentIndex(6)
        self.client_socket.send(message.encode())
        self.invite_message_label.hide()
        self.invite_accept_btn.hide()
        self.invite_reject_btn.hide()


    def invite_client(self):
        for i in range (1,5) :
            if self.rminfolist[i] == "대기" :
                invite_pop = invite_Popup(self)
                invite_pop.exec_()
                break

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
            elif signal[-6:]  == "000010" : # 방 정보 불러오기
                self.rminfolist = json.loads(signal[:-6])
                self.follow_up_game_room_refresh()
            elif signal[-6:] =='846574' : #초대를 받았을때
                self.invited_room_info = json.loads(signal[:-6])
                self.invited_action()
            elif signal[-6:] =='828282' : #게임 관련 신호를 받았을때
                self.game_play_info = json.loads(signal[:-6])
                self.game_play_client()
    def game_play_client(self):
        # tempdata = ["Game_Start",f"<SYSTEM> 게임이 시작 되었습니다.차례는 {self.order}부터 시작합니다",f"<SYSTEM>제시어는 {word}입니다.",word]
        if self.game_play_info[0] == "Game_Start" :
            self.game_start_for_all()
        # tempdata = ["Next_turn", f"<SYSTEM> 다음 차례는 {self.order+1}번 유저입니다.",f"<SYSTEM>단어는 {word}입니다.", word,new_room_turn]
        elif self.game_play_info[0] == "Next_turn" :
            self.game_next_turn()
        # tempdata = ["Game_finish", f"<SYSTEM> 잘못된 단어를 입력 하셨습니다.", f"<SYSTEM>{self.order}번 유저의 패배 ! .", word]
        elif self.game_play_info[0] == "Game_finish" :
            self.game_finish()

    def set_user_label_stylesheet(self):
        turn = int(self.Turn_lbl.text())
        current_people = int(self.current_people_lbl.text())
        self.game_order = turn % current_people
        if self.game_order == 0 :
            self.game_order = current_people
        if self.game_order  == 1 :
            self.user_1_label.setStyleSheet("background-color: #8977AD")
            self.user_2_label.setStyleSheet("background-color: #FFFFFF")
            self.user_3_label.setStyleSheet("background-color: #FFFFFF")
            self.user_4_label.setStyleSheet("background-color: #FFFFFF")
        elif self.game_order  == 2 :
            self.user_1_label.setStyleSheet("background-color: #FFFFFF")
            self.user_2_label.setStyleSheet("background-color: #8977AD")
            self.user_3_label.setStyleSheet("background-color: #FFFFFF")
            self.user_4_label.setStyleSheet("background-color: #FFFFFF")
        elif self.game_order  == 3 :
            self.user_1_label.setStyleSheet("background-color: #FFFFFF")
            self.user_2_label.setStyleSheet("background-color: #FFFFFF")
            self.user_3_label.setStyleSheet("background-color: #8977AD")
            self.user_4_label.setStyleSheet("background-color: #FFFFFF")
        elif self.game_order  == 4 :
            self.user_1_label.setStyleSheet("background-color: #FFFFFF")
            self.user_2_label.setStyleSheet("background-color: #FFFFFF")
            self.user_3_label.setStyleSheet("background-color: #FFFFFF")
            self.user_4_label.setStyleSheet("background-color: #8977AD")


    def game_next_turn(self):
        self.follow_up_list_widget.addItem(self.game_play_info[2])
        self.follow_up_list_widget.addItem(self.game_play_info[1])
        self.Turn_lbl.setText(str(self.game_play_info[4]))
        self.set_user_label_stylesheet()
        self.follow_up_word_lbl.setText(self.game_play_info[3])


    def game_finish(self):
        self.follow_up_list_widget.addItem(self.game_play_info[2])
        self.follow_up_list_widget.addItem(self.game_play_info[1])
        self.user_1_label.setStyleSheet("background-color: #FFFFFF")
        self.user_2_label.setStyleSheet("background-color: #FFFFFF")
        self.user_3_label.setStyleSheet("background-color: #FFFFFF")
        self.user_4_label.setStyleSheet("background-color: #FFFFFF")
        self.follow_up_word_lbl.setText(self.game_play_info[3])
        self.Turn_lbl.setText(str(1))
        self.follow_up_invite_btn.show()
        self.follow_up_start_btn.show()
        self.show_main6.show()


    def game_start_for_all(self):
        self.follow_up_list_widget.addItem(self.game_play_info[1])
        self.follow_up_list_widget.addItem(self.game_play_info[2])
        self.user_1_label.setStyleSheet("background-color: #8977AD")
        self.follow_up_word_lbl.setText(self.game_play_info[3])
        self.follow_up_invite_btn.hide()
        self.follow_up_start_btn.hide()
        self.show_main6.hide()

    def game_start(self):
        if self.id != self.user_1_label.text() :
            QMessageBox.critical(self, "시작 오류", "방장이 아님")
            return
        rm_number = self.follow_up_rm_number.text()
        Turn = self.Turn_lbl.text()
        game_user_num = self.current_people_lbl.text()
        game_info = ["START",rm_number,Turn,game_user_num]
        tempdata = json.dumps(game_info)
        message = tempdata + "828282" #게임 관련 식별 코드
        self.client_socket.send(message.encode())

    def invited_action(self):
        self.invite_message_label.show()
        self.invite_accept_btn.show()
        self.invite_reject_btn.show()

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
        self.client_id_lbl.setText(self.id)
        for i in range (1,5) :
            if self.rminfolist[i] == "대기" :
                self.current_people_lbl.setText(str(i-1))
                break
        print("게임방 정보 갱신")
class invite_Popup(QDialog,form_class3):

    def __init__(self,parent):
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        self.tableWidget.setRowCount(len(self.parent.idlist))
        self.tableWidget.setColumnCount(1)
        for i in range(len(self.parent.idlist)):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(str(self.parent.idlist[i])))
        self.invite_btn.clicked.connect(self.invite_user)

    def invite_user(self):
        selected_user = self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
        roomnumber = self.parent.follow_up_rm_number.text()
        tempdata = [selected_user,roomnumber]
        senddata = json.dumps(tempdata)
        if self.parent.id == selected_user :
            QMessageBox.critical(self, "초대 오류", "자기 자신은 초대하지 못합니다.")
            return
        message = senddata + "753357"
        self.parent.client_socket.send(message.encode())
        self.close()

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


#!@!@#@!
if __name__ == "__main__":
    ip, port = "127.0.0.1", 9048


    app = QApplication(sys.argv)
    mainWindow = Main(ip,port)
    mainWindow.setFixedWidth(1024)
    mainWindow.setFixedHeight(1000)
    mainWindow.show()
    app.exec_()