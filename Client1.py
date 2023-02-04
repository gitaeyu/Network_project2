from socket import *
from threading import *
import json
from PyQt5.QtWidgets import *
from PyQt5 import uic
from os import environ
from game import *

form_class = uic.loadUiType('./untitled.ui')[0]
form_class2 = uic.loadUiType('./create_room.ui')[0]
form_class3 = uic.loadUiType('./invite.ui')[0]


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
        self.test_btn2.clicked.connect(self.chat_list_view)
        self.main_login_btn.clicked.connect(self.show_login)
        self.main_sign_in_btn.clicked.connect(self.show_sign_in)
        self.main_chat_btn.clicked.connect(self.show_chat)
        self.main_game2_btn.clicked.connect(self.show_game2)
        self.show_main1.clicked.connect(self.show_main)
        self.show_main2.clicked.connect(self.show_main)
        self.show_main3.clicked.connect(self.show_main)
        self.show_main4.clicked.connect(self.show_main)
        self.show_main5.clicked.connect(self.show_main)

        self.id_same_check = False
        self.id_same_btn.clicked.connect(self.id_same)
        self.id_edit.textChanged.connect(self.id_edit_change)
        self.sign_btn.clicked.connect(self.sign_in)

        self.login_state = False
        self.user_id = ""
        self.login_btn.clicked.connect(self.login)

        self.game_status = False
        self.connect_person_list2.itemClicked.connect(self.a)
        self.attend_btn.clicked.connect(self.attend_request)
        self.game_chat_btn.clicked.connect(self.game_chat_send)
        self.game_start_btn.clicked.connect(self.game_start)
        self.stackedWidget.setCurrentIndex(1)
        self.message_send_btn.clicked.connect(self.send_chat_gt)
        self.client_create_rm_btn.clicked.connect(self.create_rm_client)
        self.follow_up_invite_btn.clicked.connect(self.invite_client)
        self.idlist = []
        self.gameidlist = []
        self.join_game_btn.clicked.connect(self.join_fu_game)
        self.show_main6.clicked.connect(self.exit_game_room)
        self.invite_accept_btn.clicked.connect(self.invite_accept2)
        self.invite_reject_btn.clicked.connect(self.invite_reject)
        self.follow_up_start_btn.clicked.connect(self.fu_game_start)
        self.invite_message_label.hide()
        self.invite_accept_btn.hide()
        self.invite_reject_btn.hide()
        self.follow_up_send_lineEdit.setText("")
        self.follow_up_send_btn.clicked.connect(self.word_send)
        self.fu_game_move.clicked.connect(self.move_fu_game_index)

    # 공룡게임 시작
    def game_start(self):
        self.client_socket.send("013".encode('utf-8'))

    # 공룡게임 채팅방에서 서버로 Send
    def game_chat_send(self):
        text = self.text_edit2.text()
        if self.game_status == True:
            if text == 'ㅇㅇ':
                self.chat_view_list2.scrollToBottom()
                self.text_edit2.clear()
                self.game_status = False
                self.client_socket.send(('\'' + self.user_id + '\'님이 게임에 참가하셨습니다.' + "011").encode('utf-8'))
                self.client_socket.send((self.user_id + "012").encode('utf-8'))
            elif text == 'ㄴㄴ':
                self.chat_view_list2.scrollToBottom()
                self.text_edit2.clear()
                self.game_status = False
            else:
                self.chat_view_list2.addItem("ㅇㅇ/ㄴㄴ로 대답하시오")
                self.chat_view_list2.scrollToBottom()
                self.text_edit2.clear()
        else:
            text = self.text_edit2.text()
            self.chat_view_list2.scrollToBottom()
            self.text_edit2.clear()
            self.client_socket.send((self.user_id + ': ' + text + "011").encode('utf-8'))

    # 목록에서 선택한 사람으로 라벨을 바꿔줌.
    def attend_request(self):
        text = self.connect_person_list2.selectedItems()
        for item in text:
            name = item.text()
        self.client_socket.send((name + "010").encode('utf-8'))

    # 목록에서 선택한 사람으로 라벨을 바꿔줌.
    def a(self):
        text = self.connect_person_list2.selectedItems()
        for item in text:
            name = item.text()
        self.attend_label.setText(name)

    # 공룡게임방으로 이동함.
    def show_game2(self):
        if self.login_state == True:
            self.stackedWidget.setCurrentIndex(5)
        else:
            self.login_label2.setText("로그인을 해주세요")

    # 로그인
    def login(self):
        self.id = self.login_id_edit.text()
        password = self.login_password_edit.text()
        sendlist = [self.id, password]
        tempdata = json.dumps(sendlist)
        send_message = tempdata + "654321"
        self.client_socket.send(send_message.encode())
        self.client_socket.send(
            ("[\"" + self.login_id_edit.text() + "\",\"" + self.login_password_edit.text() + "\"]" + "009").encode(
                'utf-8'))

    # 중복 확인 결과에 따라 아이디 중복 상태를 나타내준다.
    def sign_in(self):
        self.sign_label.clear()
        if self.id_same_check == False:
            self.sign_label.setText("아이디 중복 확인")
        if self.password1_edit.text() == self.password2_edit.text():
            self.client_socket.send(
                ("[\"" + self.id_edit.text() + "\",\"" + self.password1_edit.text() + "\"]" + "008").encode('utf-8'))
            self.sign_label.setText("가입 완료")
            self.id_edit.clear()
            self.password1_edit.clear()
            self.password2_edit.clear()
        else:
            self.sign_label.setText("비번 중복 확인")

    # 중복 확인 결과에 따라 아이디 중복 상태를 나타내준다.
    def id_edit_change(self):
        self.id_same_check = False
        self.id_same_label.setText("아이디 중복 NG")

    # 아이디가 같으면 서버로 보내는 메세지 메서드
    def id_same(self):
        self.client_socket.send((self.id_edit.text() + "007").encode('utf-8'))

    def show_chat(self):
        """
        자유 채팅방으로 이동하는 메서드
        """
        if self.login_state == True:
            self.stackedWidget.setCurrentIndex(3)
        else:
            self.login_label2.setText("로그인을 해주세요")

    def show_sign_in(self):
        """
        회원가입 창으로 이동하는 메서드
        :return:
        """
        self.stackedWidget.setCurrentIndex(2)

    def show_login(self):
        """
        로그인 상태 유무에 따라
        UI의 상태를 변경해준다.
        :return:
        """
        if self.login_state == False:
            self.stackedWidget.setCurrentIndex(1)
        elif self.login_state == True:
            self.login_state = False
            self.client_socket.send((self.user_id + "006").encode('utf-8'))
            self.main_login_label.setText("")
            self.main_login_btn.setText("로그인")

    def show_main(self):
        """
        메인으로 돌아옴
        """
        self.stackedWidget.setCurrentIndex(0)
        self.login_label.setText("")

    def closeEvent(self, QCloseEvent):
        """
        창을 닫을때 일정 신호를 보내줌.
        """
        self.exit_game_room()
        self.client_socket.send((self.user_id + "006").encode('utf-8'))
        time.sleep(0.2)
        self.client_socket.send("!@$#@#Socke@$close".encode())
        QCloseEvent.accept()

    def add_chat_room(self):
        """
        채팅방을 등록시 해당 이름을 서버로 보낸다.
        """
        chat_name = self.chat_room_add_edit.text()
        self.client_socket.send((chat_name + "003").encode('utf-8'))  # 채팅 룸 추가 코드 003
        self.chat_room_add_edit.clear()

    def chat_list_view(self):
        """
        체팅방 리스트를 보여주는 메서드
        """
        self.chat_room_list.clear()
        self.client_socket.send("002".encode('utf-8'))

    def chat_view(self):
        """
        채팅방 선택시에 그에 따른 채팅방의 이름을 서버로 전달하고
        다시 수신받고 그 채팅방의 내역을 불러온다.
        """
        room_text = self.chat_room_list.selectedItems()
        for item in room_text:
            room_name = item.text()
        self.client_socket.send((room_name + "004").encode('utf-8'))  # 클라이언트의 선택된 채팅 룸이름을 알려주기 위함.
        self.chat_view_list.clear()
        self.client_socket.send((room_name + "001").encode('utf-8'))

    def initialize_socket(self, ip, port):
        """
        클라이언트 소켓을 열고 서버 소켓과 연결해준다.
        """
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        remote_ip = ip
        remote_port = port
        self.client_socket.connect((remote_ip, remote_port))

    def send_chat(self):
        """
        자유 채팅방에서의 채팅을 보내주는 메서드
        """
        senders_name = self.user_id
        data = self.text_edit.text()
        message = (senders_name + ': ' + data + "000").encode('utf-8')
        self.client_socket.send(message)
        self.text_edit.clear()
        self.chat_view_list.scrollToBottom()
        return 'break'

    def send_chat_gt(self):
        """
        끝말잇기 게임 대기방에서의 채팅을 보내주는 메서드
        """
        senders_name = self.id
        data = self.game_lineEdit.text()
        message = (senders_name + ': ' + data + '123456').encode('utf-8')
        self.client_socket.send(message)
        self.game_lineEdit.clear()
        return 'break'

    def listen_thread(self):
        """
        서버에서의 신호를 수신받는 스레드 시작
        """
        t = Thread(target=self.receive_message, args=(self.client_socket,))
        t.daemon = True
        t.start()

    def receive_message(self, so):
        """
        서버에서 전달하는 메시지를 수신하는 스레드
        """
        while True:
            try:
                print("스레드 시작")
                buf = so.recv(1024)
                text = buf.decode('utf-8')
                print(text)
            except:
                break
            else:
                if not buf:  # 연결 종료 됨
                    print("연결종료됨")
                    break
                if text[-3:] == '000':  # 메시지 송수신
                    self.chat_view_list.addItem(text[:-3])
                elif text[-3:] == '001':  # 채팅 불러오기
                    self.chat_view_list.scrollToBottom()
                    self.chat_view_list.addItem(text[:-3])
                    self.chat_view_list.scrollToBottom()
                elif text[-3:] == '002':  # 채팅방 목록 불러오기
                    print("채팅방 목록 불러오기")
                    self.chat_room_list.addItem(text[:-3])
                elif text[-3:] == '005':
                    print("b")
                    self.connect_person_list.clear()
                    self.connect_person_list2.clear()
                    result_list = eval(text[:-3])
                    for x in result_list:
                        self.connect_person_list.addItem(str(x))
                        self.connect_person_list2.addItem(str(x))
                elif text[-3:] == '007':
                    if '1' == text[:-3]:
                        self.id_same_check = False
                        self.id_same_label.setText("아이디 중복 NG")
                    else:
                        self.id_same_check = True
                        self.id_same_label.setText("아이디 중복 OK")
                elif text[-3:] == '009':
                    if 'noneID' == text[:-3]:
                        self.login_label.setText("아이디없음")
                        print("아이디 없음")
                    elif 'ok' == text[:-3]:
                        print("ok")
                        self.login_state = True
                        self.login_label.setText("로그인성공")
                        self.main_login_label.setText("'" + self.login_id_edit.text() + "'님이 로그인 하셨습니다.")
                        self.user_id = self.login_id_edit.text()
                        self.main_login_btn.setText("로그아웃")
                        self.login_id_edit.clear()
                        self.login_password_edit.clear()
                        self.client_socket.send((self.user_id + "005").encode('utf-8'))
                        self.stackedWidget.setCurrentIndex(0)
                    elif 'nonePassword' == text[:-3]:
                        self.login_label.setText("비밀번호NG")
                elif text[-3:] == '010':
                    if text[:-3] == self.user_id:
                        self.chat_view_list2.scrollToBottom()
                        self.chat_view_list2.addItem("'" + text[:-3] + "'" + "님 게임에 참가하시겠습니까?")
                        self.chat_view_list2.scrollToBottom()
                        self.game_status = True
                elif text[-3:] == '011':
                    self.chat_view_list2.addItem(text[:-3])
                    self.chat_view_list2.scrollToBottom()
                elif text[-3:] == '012':
                    self.connect_person_list3.clear()
                    result_list = eval(text[:-3])
                    for x in result_list:
                        self.connect_person_list3.addItem(str(x))
                elif text[-3:] == '013':
                    result_list = eval(text[:-3])
                    for x in result_list:
                        if x == self.user_id:
                            score = main2()
                            self.client_socket.send((self.user_id + ": " + str(score) + "점!!!011").encode('utf-8'))
                            self.client_socket.send((self.user_id + "014").encode('utf-8'))
                elif text[-3:] == '015':
                    self.connect_person_list3.clear()
                elif text[-6:] == "123456":
                    self.textBrowser.append(text[:-6] + '\n')
                elif text[-6:] == "985674":
                    self.idlist = json.loads(text[:-6])
                    print(self.idlist)
                    self.tableWidget.setRowCount(len(self.idlist))
                    self.tableWidget.setColumnCount(1)
                    for i in range(len(self.idlist)):
                        self.tableWidget.setItem(i, 0, QTableWidgetItem(str(self.idlist[i])))
                elif text[-6:] == "100109":
                    self.roomlist = json.loads(text[:-6])
                    if self.roomlist != []:
                        self.tableWidget_4.setRowCount(len(self.roomlist))
                        self.tableWidget_4.setColumnCount(len(self.roomlist[0]))
                        for i in range(len(self.roomlist)):
                            for j in range(len(self.roomlist[i])):
                                # i번째 줄의 j번째 칸에 데이터를 넣어줌
                                self.tableWidget_4.setItem(i, j, QTableWidgetItem(str(self.roomlist[i][j])))
                elif text[-6:] == "100110":  # 방 정보 불러오기
                    self.rminfolist = json.loads(text[:-6])
                    self.follow_up_game_room_refresh()
                elif text[-6:] == '846574':  # 초대를 받았을때
                    self.invited_room_info = json.loads(text[:-6])
                    print(self.invited_room_info)
                    self.invited_action()
                elif text[-6:] == '828282':  # 게임 관련 신호를 받았을때
                    self.game_play_info = json.loads(text[:-6])
                    self.game_play_client()
        so.close()

    ##기태 메서드
    def game_play_client(self):
        """
        끝말잇기 게임시 정보를 수신받고 리스트 안에 들은 명령어를 통하여
        실행될 메서드를 정해준다.
        """
        # tempdata = ["Game_Start",f"<SYSTEM> 게임이 시작 되었습니다.차례는 {self.order}부터 시작합니다",f"<SYSTEM>제시어는 {word}입니다.",word]
        if self.game_play_info[0] == "Game_Start":
            self.game_start_for_all()
        # tempdata = ["Next_turn", f"<SYSTEM> 다음 차례는 {self.order+1}번 유저입니다.",f"<SYSTEM>단어는 {word}입니다.", word,new_room_turn]
        elif self.game_play_info[0] == "Next_turn":
            self.game_next_turn()
        # tempdata = ["Game_finish", f"<SYSTEM> 잘못된 단어를 입력 하셨습니다.", f"<SYSTEM>{self.order}번 유저의 패배 ! .", word]
        elif self.game_play_info[0] == "Game_finish":
            self.game_finish()

    def set_user_label_stylesheet(self):
        """
        현재 누구의 턴이냐에 따라서 게임방 UI를 변경해준다.
        :return:
        """
        turn = int(self.Turn_lbl.text())
        current_people = int(self.current_people_lbl.text())
        self.game_order = turn % current_people
        if self.game_order == 0:
            self.game_order = current_people
        if self.game_order == 1:
            self.user_1_label.setStyleSheet("background-color: #8977AD")
            self.user_2_label.setStyleSheet("background-color: #FFFFFF")
            self.user_3_label.setStyleSheet("background-color: #FFFFFF")
            self.user_4_label.setStyleSheet("background-color: #FFFFFF")
        elif self.game_order == 2:
            self.user_1_label.setStyleSheet("background-color: #FFFFFF")
            self.user_2_label.setStyleSheet("background-color: #8977AD")
            self.user_3_label.setStyleSheet("background-color: #FFFFFF")
            self.user_4_label.setStyleSheet("background-color: #FFFFFF")
        elif self.game_order == 3:
            self.user_1_label.setStyleSheet("background-color: #FFFFFF")
            self.user_2_label.setStyleSheet("background-color: #FFFFFF")
            self.user_3_label.setStyleSheet("background-color: #8977AD")
            self.user_4_label.setStyleSheet("background-color: #FFFFFF")
        elif self.game_order == 4:
            self.user_1_label.setStyleSheet("background-color: #FFFFFF")
            self.user_2_label.setStyleSheet("background-color: #FFFFFF")
            self.user_3_label.setStyleSheet("background-color: #FFFFFF")
            self.user_4_label.setStyleSheet("background-color: #8977AD")

    def game_next_turn(self):
        """
        게임이 끝나지 않고 정상적으로 진행 됬을 시에
        채팅창에 시스템 채팅을 추가해주며 UI가 변경됨
        """
        self.follow_up_list_widget.addItem(self.game_play_info[2])
        self.follow_up_list_widget.addItem(self.game_play_info[1])
        self.Turn_lbl.setText(str(self.game_play_info[4]))
        self.set_user_label_stylesheet()
        self.follow_up_word_lbl.setText(self.game_play_info[3])

    def game_finish(self):
        """
        게임이 끝났을 시에 UI를 초기 상태로 변경해준다.
        """
        self.follow_up_list_widget.addItem(self.game_play_info[2])
        self.follow_up_list_widget.addItem(self.game_play_info[1])
        self.user_1_label.setStyleSheet("background-color: #FFFFFF")
        self.user_2_label.setStyleSheet("background-color: #FFFFFF")
        self.user_3_label.setStyleSheet("background-color: #FFFFFF")
        self.user_4_label.setStyleSheet("background-color: #FFFFFF")
        self.follow_up_word_lbl.setText(self.game_play_info[3])
        self.follow_up_word_lbl.setStyleSheet("color: red")
        self.Turn_lbl.setText(str(1))
        self.follow_up_invite_btn.show()
        self.follow_up_start_btn.show()
        self.show_main6.show()

    def game_start_for_all(self):
        """
        서버로부터 게임 시작 신호를 받았을 때에 실행되는 메서드
        시작 초대 등의 UI가 사라진다.
        """
        self.follow_up_list_widget.addItem(self.game_play_info[1])
        self.follow_up_list_widget.addItem(self.game_play_info[2])
        self.user_1_label.setStyleSheet("background-color: #8977AD")
        self.follow_up_word_lbl.setText(self.game_play_info[3])
        self.follow_up_invite_btn.hide()
        self.follow_up_start_btn.hide()
        self.show_main6.hide()

    def fu_game_start(self):
        """
        게임 유저가 시작을 눌렀을시에 발생하는 메서드로
        1번 유저가 게임 시작을 누르면 서버로 신호를 발송한다.
        """
        if self.id != self.user_1_label.text():
            QMessageBox.critical(self, "시작 오류", "방장이 아님")
            return
        rm_number = self.follow_up_rm_number.text()
        Turn = self.Turn_lbl.text()
        game_user_num = self.current_people_lbl.text()
        game_info = ["START", rm_number, Turn, game_user_num]
        tempdata = json.dumps(game_info)
        message = tempdata + "828282"  # 게임 관련 식별 코드
        self.client_socket.send(message.encode())

    def invited_action(self):
        """
        게임에 초대받았을때 나타난다.
        """
        self.invite_message_label.show()
        self.invite_accept_btn.show()
        self.invite_reject_btn.show()

    def join_fu_game(self):
        """
        끝말잇기 게임방에 들어갔을시에 실행되는 메서드로
        선택한 방의 정보를 서버로 보내고 서버는 이에 맞게 클라이언트들에게 방 리스트와
        들어간 방의 정보를 다시 보내준다.
        """
        selected_rm_number = self.tableWidget_4.item(self.tableWidget_4.currentRow(), 0).text()
        selected_people = self.tableWidget_4.item(self.tableWidget_4.currentRow(), 2).text()
        max_people = self.tableWidget_4.item(self.tableWidget_4.currentRow(), 3).text()
        if selected_people == max_people:
            QMessageBox.critical(self, "인원 꽉참", "방을 만들거나 다른 방에 접속해주세요")
            return
        select_rm_info = [selected_rm_number, selected_people, self.id]
        tempdata = json.dumps(select_rm_info)
        message = tempdata + "000111"
        self.stackedWidget.setCurrentIndex(6)
        self.client_id_lbl.setText(self.id)
        self.follow_up_list_widget.clear()
        self.follow_up_word_lbl.setText("제시어")
        self.client_socket.send(message.encode())

    def follow_up_game_room_refresh(self):
        """
        서버에서 정보를 수신하고 끝말잇기 방의 상태를 갱신한다.
        """
        self.follow_up_rm_number.setText(str(self.rminfolist[0]))
        self.user_1_label.setText(self.rminfolist[1])
        self.user_2_label.setText(self.rminfolist[2])
        self.user_3_label.setText(self.rminfolist[3])
        self.user_4_label.setText(self.rminfolist[4])
        self.client_id_lbl.setText(self.id)
        for i in range(1, 5):
            if self.rminfolist[i] == "대기":
                self.current_people_lbl.setText(str(i - 1))
                break
        print("게임방 정보 갱신")

    def word_send(self):
        """
        끝말잇기 방에서 친 단어를 전달해준다.
        만약 앞의 단어 끝글자가 아닌 글자를 입력시에는 실패했다는 정보를 보내줌
        """
        prev_word = self.follow_up_word_lbl.text()
        word = self.follow_up_send_lineEdit.text()
        if self.client_id_lbl.text() == self.user_1_label.text():
            self.order = 1
        elif self.client_id_lbl.text() == self.user_2_label.text():
            self.order = 2
        elif self.client_id_lbl.text() == self.user_3_label.text():
            self.order = 3
        elif self.client_id_lbl.text() == self.user_4_label.text():
            self.order = 4
        turn = int(self.Turn_lbl.text())
        current_people = int(self.current_people_lbl.text())
        self.game_order = turn % current_people
        if self.game_order == 0:
            self.game_order = current_people
        if self.order != self.game_order:
            QMessageBox.critical(self, "차례 아님", "턴을 기다려주세요")
            return
        elif prev_word[-1] != word[0]:
            rm_number = self.follow_up_rm_number.text()
            game_info = ["FAIL", rm_number, turn, current_people, word]
            tempdata = json.dumps(game_info)
            message = tempdata + "828282"  # 게임 관련 식별 코드
            self.client_socket.send(message.encode())
        else:
            rm_number = self.follow_up_rm_number.text()
            game_info = ["CHECK", rm_number, turn, current_people, word]
            tempdata = json.dumps(game_info)
            message = tempdata + "828282"  # 게임 관련 식별 코드
            self.client_socket.send(message.encode())

    def invite_reject(self):
        """
        초대 거부시에 초대 UI 사라짐
        """
        self.invite_message_label.hide()
        self.invite_accept_btn.hide()
        self.invite_reject_btn.hide()

    def invite_accept2(self):
        """
        초대 수락시에 초대한 방에 들어가게 되는 메서드
        그에 맞게 UI가 변경되고 정보를 송신한다.
        """
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
        message = tempdata + "000111"
        self.stackedWidget.setCurrentIndex(6)
        self.client_socket.send(message.encode())
        self.invite_message_label.hide()
        self.invite_accept_btn.hide()
        self.invite_reject_btn.hide()

    def move_fu_game_index(self):
        """
        끝말잇기 UI로 이동하는 메서드
        """
        if self.login_state == True:
            self.stackedWidget.setCurrentIndex(4)
        else:
            self.login_label2.setText("로그인을 해주세요")

    def invite_client(self):
        """
        대기 칸이 열려있어야만 초대를 할수 있다.
        """
        for i in range(1, 5):
            if self.rminfolist[i] == "대기":
                invite_pop = invite_Popup(self)
                invite_pop.exec_()
                break

    def exit_game_room(self):
        """
        끝말잇기 게임방을 나갔을때 해당 방의 정보를 서버로 송신하고
        페이지를 이동한다.
        """
        roomnumber = self.follow_up_rm_number.text()
        user_1id = self.user_1_label.text()
        user_2id = self.user_2_label.text()
        user_3id = self.user_3_label.text()
        user_4id = self.user_4_label.text()

        exit_room_info = [roomnumber, user_1id, user_2id, user_3id, user_4id, self.id]
        tempdata = json.dumps(exit_room_info)
        message = tempdata + "000113"
        self.stackedWidget.setCurrentIndex(4)
        self.client_socket.send(message.encode())

    def create_rm_client(self):
        """
        방만들기 UI를 띄워줌
        """
        createpop = Popup(self)
        createpop.exec_()


class invite_Popup(QDialog, form_class3):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        self.tableWidget.setRowCount(len(self.parent.idlist))
        self.tableWidget.setColumnCount(1)
        for i in range(len(self.parent.idlist)):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(str(self.parent.idlist[i])))
        self.invite_btn.clicked.connect(self.invite_user)

    def invite_user(self):
        """
        초대하기 버튼을 누르면 해당하는 멤버에게 서버를 통해 초대 메시지를 송신한다.
        """
        selected_user = self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
        roomnumber = self.parent.follow_up_rm_number.text()
        tempdata = [selected_user, roomnumber]
        senddata = json.dumps(tempdata)
        if self.parent.id == selected_user:
            QMessageBox.critical(self, "초대 오류", "자기 자신은 초대하지 못합니다.")
            return
        message = senddata + "753357"
        self.parent.client_socket.send(message.encode())
        self.close()


class Popup(QDialog, form_class2):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        self.create_rm_btn.clicked.connect(self.create_room)

    def create_room(self):
        """
        방을 만들고 그 정보를 서버로 송신한다.
        """
        name = self.room_naming_lineEdit.text()
        gamekind = self.game_kind_cb.currentText()
        numpeople = self.num_people_cb.currentText()
        id = self.parent.id
        roominfo = [name, gamekind, numpeople, id]
        tempdata = json.dumps(roominfo)
        message = tempdata + "100108"
        self.parent.stackedWidget.setCurrentIndex(6)
        self.parent.client_socket.send(message.encode())
        self.close()


if __name__ == "__main__":
    ip = '127.0.0.1'
    port = 9048

    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCREEN_FACTOR"] = "1"

    app = QApplication(sys.argv)
    mainWindow = Main(ip, port)
    mainWindow.show()
    app.exec_()