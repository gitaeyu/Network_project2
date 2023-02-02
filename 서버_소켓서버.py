import socketserver
import pymysql
import time
import json


host_str = '10.10.21.112'
user_str = 'root3'
password_str = '123456789'

class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        (ip, port) = self.client_address
        client = self.request, (ip, port)
        if client not in Multi_server.clients :
            Multi_server.clients.append(client)
        print(ip, ":", str(port), '가 연결되었습니다.')
        Multi_server.receive_messages(self.request)
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class MultiChatServer:

    #소켓을 생성하고 연결되면 accept_client() 호출

    def __init__(self):
        self.idlist = []
        self.clients = []
        self.user_list = []
        self.game_list = []
        self.game_player_list = []
        self.final_received_message = "" #최종 수신 메시지
        self.room_select = "chat_all"


    #데이터를 수신하여 모든 클라이언트에게 전송한다.
    def receive_messages(self,socket):
        while True:
            try:
                incoming_message = socket.recv(1024)
                self.recv_signal = incoming_message
                if not incoming_message : #연결이 종료됨
                    break
            except ConnectionAbortedError :
                self.remove_socket(socket)
                socket.close()
                break
            else:
                self.final_received_message = incoming_message.decode('utf-8')
                print(self.final_received_message)
                # DB에 수신 메시지 넣어줌
                if self.final_received_message[-3:] == '000':
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='multi_network_server', charset='utf8')
                    with con:
                        with con.cursor() as cur:
                            sql = f"INSERT INTO {self.room_select} values('{self.final_received_message}')"
                            cur.execute(sql)
                            con.commit()
                    ###################################################### Data base 접속 end
                if self.final_received_message[-3:] in ('000','010','011'):               # 채팅창 불러오기 code
                    self.send_all_clients(socket)
                elif self.final_received_message[-3:] == '001':               # 채팅창 불러오기 code
                    self.show_chat(socket)
                elif self.final_received_message[-3:] == '002':             # 채팅방 목록 불러오기 code
                    self.show_chat_room_list(socket)
                elif self.final_received_message[-3:] == '003':  # 채팅방 추가 code
                    self.add_chat_room()
                elif self.final_received_message[-3:] == '004':  # 채팅방 이름 서버에 전달하는 code
                    self.choice_chat_room()
                elif self.final_received_message[-3:] == '005':
                    self.connect_user()
                elif self.final_received_message[-3:] == '006':
                    self.disconnect_user()
                elif self.final_received_message[-3:] == '007':
                    self.id_same(socket)
                elif self.final_received_message[-3:] == '008':
                    self.sign_in()
                elif self.final_received_message[-3:] == '009':
                    self.login(socket)
                elif self.final_received_message[-3:] == '012':
                    self.game_player_rec()
                elif self.final_received_message[-3:] == '013':
                    self.game_player_send()
                elif self.final_received_message[-3:] == '014':
                    self.game_player_list.remove(self.final_received_message[:-3])
                    if len(self.game_player_list) == 0:
                        for client in self.clients:
                            socket, (ip, port) = client
                            socket.sendall("015".encode())
                elif self.recv_signal.decode()[-6:] == "654321":
                    self.login_check(socket)
                elif self.recv_signal.decode()[-6:] == "123456":
                    self.receive_messages_gt(socket)
                elif self.recv_signal.decode()[-6:] == "753357":
                    self.invite_signal_send(socket)
                elif self.recv_signal.decode()[-6:] == "100108":
                    self.create_room_save_db(socket)
                elif self.recv_signal.decode()[-6:] == "000111":
                    self.client_join_room(socket)
                elif self.recv_signal.decode()[-6:] == "000113":
                    self.exit_game_room(socket)
                elif self.recv_signal.decode()[-6:] == "828282":
                    self.fu_game_play(socket)
                elif self.recv_signal.decode() == "!@$#@#Socke@$close":
                    self.remove_socket(socket)

    #송신 클라이언트를 제외한 모든 클라이언트에게 메세지 전송
    def send_all_clients(self, senders_socket):
        for client in self.clients: #목록에 있는 모든 소켓에 대해
            print(client)
            socket, (ip,port) = client
            if socket is not senders_socket: #송신 클라이언트는 제외
                try:
                    if self.final_received_message[-3:] == '000':
                        socket.sendall((self.final_received_message[:-3]+'000').encode())
                    if self.final_received_message[-3:] == '010':
                        self.game_list.append(self.final_received_message[:-3])
                        socket.sendall((self.final_received_message[:-3] + "010").encode())
                    if self.final_received_message[-3:] == '011':
                        socket.sendall((self.final_received_message[:-3] + "011").encode())
                except: #연결종료
                    self.clients.remove(client) #소켓 제거
                    print(f"{ip},{port} 연결이 종료 되었습니다.")
            else:
                socket.sendall(self.final_received_message.encode())



    def show_chat(self, socket):
        ###################################################### Data base 접속 start
        con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='multi_network_server',
                              charset='utf8')
        with con:
            with con.cursor() as cur:
                sql = f"SELECT * FROM {self.final_received_message[:-3]}"
                cur.execute(sql)
                rows = cur.fetchall()
        ##################################################### Data base 접속 end
        for x in rows:
            time.sleep(0.0001)
            self.final_received_message = str(x[0]) + '001'
            self.send_all_clients(socket)

    def show_chat_room_list(self, socket):
        ###################################################### Data base 접속 start
        con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='multi_network_server',
                              charset='utf8')
        with con:
            with con.cursor() as cur:
                sql = f"SHOW TABLES LIKE 'chat%'"
                cur.execute(sql)
                rows = cur.fetchall()
        ##################################################### Data base 접속 end
        for x in rows:
            time.sleep(0.0001)
            self.final_received_message = str(x[0]) + "002"
            print(self.final_received_message)
            self.send_all_clients(socket)
            print(4)


    def add_chat_room(self):
        ###################################################### Data base 접속 start
        con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='multi_network_server',
                              charset='utf8')
        with con:
            with con.cursor() as cur:
                sql = f"CREATE TABLE if not exists {self.final_received_message[:-3]}(text TEXT) ENGINE= InnoDB CHARSET=utf8mb4;"
                cur.execute(sql)
                con.commit()
        ###################################################### Data base 접속 end

    def choice_chat_room(self):
        self.room_select = self.final_received_message[:-3]

    def connect_user(self):
        self.user_list.append(self.final_received_message[:-3])
        for client in self.clients:
            socket, (ip, port) = client
            socket.sendall((str(self.user_list) + "005").encode())

    def disconnect_user(self):
        self.user_list.remove(self.final_received_message[:-3])
        for client in self.clients:
            socket, (ip, port) = client
            socket.sendall((str(self.user_list) + "005").encode())

    def id_same(self, socket):
        ###################################################### Data base 접속 start
        con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='multi_network_server', charset='utf8')
        with con:
            with con.cursor() as cur:
                sql = f"SELECT * FROM memberinfo where ID = '{self.final_received_message[:-3]}';"
                cur.execute(sql)
                rows = cur.fetchall()
        ##################################################### Data base 접속 end
        self.final_received_message = str(len(rows)) + "007"
        self.send_all_clients(socket)

    def sign_in(self):
        a = eval(self.final_received_message[:-3])
        ###################################################### Data base 접속 start
        con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='multi_network_server', charset='utf8')
        with con:
            with con.cursor() as cur:
                sql = f"INSERT INTO memberinfo values('{str(a[0])}','{str(a[1])}','')"
                cur.execute(sql)
                con.commit()
        ###################################################### Data base 접속 end

    def login(self, socket):
        a = eval(self.final_received_message[:-3])
        ###################################################### Data base 접속 start
        con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='multi_network_server',
                              charset='utf8')
        with con:
            with con.cursor() as cur:
                sql = f"SELECT * FROM memberinfo where ID = '{a[0]}';"
                cur.execute(sql)
                rows = cur.fetchall()
        ##################################################### Data base 접속 end
        if len(rows) == 0:
            socket.sendall(("noneID" + "009").encode())
            print("아이디 없음")
        else:
            for x in rows:
                print(x)
                if x[0] == a[0] and x[1] == a[1]:
                    socket.sendall(("ok" + "009").encode())
                    print("ok")
                else:
                    socket.sendall(("nonePassword" + "009").encode())
                    print("nonePassword")

    def game_player_rec(self):
        self.game_player_list.append(self.final_received_message[:-3])
        for client in self.clients:
            socket, (ip, port) = client
            socket.sendall((str(self.game_player_list) + "012").encode())

    def game_player_send(self):
        for client in self.clients:
            socket, (ip, port) = client
            socket.sendall((str(self.game_player_list) + "013").encode())
    def fu_game_play(self,c_socket):
        self.fu_game_play_info = json.loads(self.recv_signal.decode()[:-6])
        print(self.fu_game_play_info)
        if self.fu_game_play_info[0] == "START":
            self.fu_game_start(c_socket)
        elif self.fu_game_play_info[0] == "CHECK" : # game_info = ["CHECK", rm_number, turn, current_people,word]
            self.fu_game_word_check(c_socket)
        elif self.fu_game_play_info[0] == "FAIL" : #game_info = ["FAIL", rm_number, turn, current_people,word]
            self.fu_game_finish(c_socket)

    def fu_game_finish(self,c_socket):
        room_number = self.fu_game_play_info[1]
        room_turn = self.fu_game_play_info[2]
        room_people_num = self.fu_game_play_info[3]
        word = self.fu_game_play_info[4]
        self.order = int(room_turn) % int(room_people_num)
        if self.order == 0 :
            self.order = int(room_people_num)
        tempdata = ["Game_finish", f"<SYSTEM> 잘못된 단어를 입력 하셨습니다.",
                    f"<SYSTEM>{self.order}번 유저의 패배 ! .", word]
        senddata = json.dumps(tempdata) + "828282"
        con = pymysql.connect(host='10.10.21.112', user="root3", password="123456789", db='multi_network_server',
                              charset='utf8')
        with con:
            with con.cursor() as cur:
                cur.execute(f"select * from game_room_people where Number = {room_number}")
                selected_room_info = cur.fetchall()
                cur.execute(f"insert into fu_game_result (result{self.order}, id_1, id_2, id_3, id_4) values \
                            ('패배','{selected_room_info[0][1]}','{selected_room_info[0][2]}','{selected_room_info[0][3]}'\
                            ,'{selected_room_info[0][4]}')")
                con.commit()
        # 채팅방에 있는 사람에게 정보를 전달함
        i = 0
        for id in self.idlist:  # 목록에 있는 모든 소켓에 대해
            if id == selected_room_info[0][1] or id == selected_room_info[0][2] \
                    or id == selected_room_info[0][3] or id == selected_room_info[0][4]:
                client = self.clients[i]
                socket = client[0]
                socket.sendall(senddata.encode())
            i += 1

    def fu_game_word_check(self,c_socket):
        room_number = self.fu_game_play_info[1]
        room_turn = self.fu_game_play_info[2]
        room_people_num = self.fu_game_play_info[3]
        word = self.fu_game_play_info[4]
        new_room_turn = int(self.fu_game_play_info[2]) + 1
        self.order = int(room_turn) % int(room_people_num)
        if self.order == 0 :
            self.order = int(room_people_num)
        con = pymysql.connect(host='10.10.21.112', user="root3", password="123456789", db='multi_network_server',
                              charset='utf8')
        with con:
            with con.cursor() as cur:
                cur.execute(f"select * from game_room_people where Number = {room_number}")
                selected_room_info = cur.fetchall()
                count = cur.execute(f"select * from kr where word = '{word}' ")
                con.commit()
        if count > 0 :
            tempdata = ["Next_turn", f"<SYSTEM> 이전 차례는 {self.order}번 유저입니다.",
                        f"<SYSTEM>단어는 {word}입니다.", word,new_room_turn]
            senddata = json.dumps(tempdata) + "828282"
        else :
            tempdata = ["Game_finish", f"<SYSTEM> 잘못된 단어를 입력 하셨습니다.",
                        f"<SYSTEM>{self.order}번 유저의 패배 ! .", word]
            senddata = json.dumps(tempdata) + "828282"
            con = pymysql.connect(host='10.10.21.112', user="root3", password="123456789", db='multi_network_server',
                                  charset='utf8')
            with con:
                with con.cursor() as cur:
                    cur.execute(f"select * from game_room_people where Number = {room_number}")
                    selected_room_info = cur.fetchall()
                    cur.execute(f"insert into fu_game_result (result{self.order}, id_1, id_2, id_3, id_4) values \
                                ('패배','{selected_room_info[0][1]}','{selected_room_info[0][2]}','{selected_room_info[0][3]}'\
                                ,'{selected_room_info[0][4]}')")
                    con.commit()

        # 채팅방에 있는 사람에게 정보를 전달함
        i = 0
        for id in self.idlist:  # 목록에 있는 모든 소켓에 대해
            if id == selected_room_info[0][1] or id == selected_room_info[0][2] \
                    or id == selected_room_info[0][3] or id == selected_room_info[0][4]:
                client = self.clients[i]
                socket = client[0]
                socket.sendall(senddata.encode())
            i += 1

    def fu_game_start(self,c_socket):
        room_number = self.fu_game_play_info[1]
        room_turn = self.fu_game_play_info[2]
        room_people_num = self.fu_game_play_info[3]
        self.order = int(room_turn) % int(room_people_num)
        word = "자동차"
        tempdata = ["Game_Start",f"<SYSTEM> 게임이 시작 되었습니다.차례는 {self.order}부터 시작합니다",
                   f"<SYSTEM>제시어는 {word}입니다.",word]
        senddata = json.dumps(tempdata) + "828282"
        con = pymysql.connect(host='10.10.21.112', user="root3", password="123456789", db='multi_network_server',
                              charset='utf8')
        with con:
            with con.cursor() as cur:
                cur.execute(f"select * from game_room_people where Number = {room_number}")
                selected_room_info = cur.fetchall()
                con.commit()
        # 채팅방에 있는 사람에게 정보를 전달함
        i = 0
        for id in self.idlist:  # 목록에 있는 모든 소켓에 대해
            if id == selected_room_info[0][1] or id == selected_room_info[0][2] \
                    or id == selected_room_info[0][3] or id == selected_room_info[0][4]:
                client = self.clients[i]
                socket = client[0]
                socket.sendall(senddata.encode())
            i += 1


    def exit_game_room(self,c_socket):
        con = pymysql.connect(host='10.10.21.112', user="root3", password="123456789", db='multi_network_server',
                              charset='utf8')
        exit_room_info = json.loads(self.recv_signal.decode()[:-6])
        self.exit_user_number = 5
        for i in range(len(exit_room_info)-1) :
            if exit_room_info[i] == exit_room_info[5] :
                self.exit_user_number = i
                break
        with con:
            with con.cursor() as cur:
                if self.exit_user_number == 1:
                    cur.execute(f"update game_room_people set user_1 = '{exit_room_info[2]}',\
                    user_2 = '{exit_room_info[3]}', user_3 ='{exit_room_info[4]}' ,user_4 ='대기' \
                    where Number = {exit_room_info[0]}")
                elif self.exit_user_number == 2:
                    cur.execute(f"update game_room_people set user_2 = '{exit_room_info[3]}',\
                    user_3 = '{exit_room_info[4]}', user_4 ='대기' where Number = {exit_room_info[0]}")
                elif self.exit_user_number == 3:
                    cur.execute(f"update game_room_people set \
                    user_3 = '{exit_room_info[4]}', user_4 ='대기' where Number = {exit_room_info[0]}")
                elif self.exit_user_number == 4:
                    cur.execute(f"update game_room_people set user_4 ='대기' where Number = {exit_room_info[0]}")
                cur.execute("delete from game_room_people where user_1 = '대기'")
                cur.execute("delete a from game_room_list as a left outer join game_room_people as b \
                            on a.Number = b.Number where b.Number is null")
                cur.execute(f"select * from game_room_people where Number = {exit_room_info[0]}")
                selected_room_info = cur.fetchall()
                cur.execute(
                    f"update game_room_list set Current_people = Current_people - 1 where Number = {exit_room_info[0]}")
                cur.execute(f"select * from game_room_list")
                rows = cur.fetchall()
                con.commit()
                tempdata = json.dumps(rows)
                senddata = tempdata + "100109"
                self.final_received_message_gt\
                    = senddata
                self.send_all_clients_gt(c_socket)
                if selected_room_info != () :
                    tempdata = json.dumps(selected_room_info[0])
                    gr_info = tempdata + "100110" #방 정보 식별 코드
                    i = 0
                    for id in self.idlist:  # 목록에 있는 모든 소켓에 대해
                        print(self.clients)
                        if id == selected_room_info[0][1] or id == selected_room_info[0][2]\
                                or id == selected_room_info[0][3] or id  == selected_room_info[0][4] :
                            client = self.clients[i]
                            socket = client[0]
                            socket.sendall(gr_info.encode())
                        i += 1
                con.commit()
    def client_join_room(self, c_socket):
        client_room_info = json.loads(self.recv_signal.decode()[:-6])
        room_number = client_room_info[0]
        room_current_people = client_room_info[1]
        client_id = client_room_info[2]
        con = pymysql.connect(host='10.10.21.112', user="root3", password="123456789", db='multi_network_server',
                              charset='utf8')
        with con:
            with con.cursor() as cur:
                sql = f"update game_room_people set user_{int(room_current_people) + 1}  = \
                                        '{client_id}' where Number = {room_number}"
                cur.execute(sql)
                cur.execute(f"select * from game_room_people where Number = {room_number}")
                selected_room_info = cur.fetchall()
                cur.execute(
                    f"update game_room_list set Current_people = Current_people + 1 where Number = {room_number}")
                cur.execute(f"select * from game_room_list")
                rows = cur.fetchall()
                con.commit()
                tempdata = json.dumps(rows)
                senddata = tempdata + "100109"
                self.final_received_message_gt\
                    = senddata
                self.send_all_clients_gt(c_socket)
                tempdata = json.dumps(selected_room_info[0])
                gr_info = tempdata + "100110" #방 정보 식별 코드
        # 채팅방에 있는 사람에게 정보를 전달함
        i = 0
        for id in self.idlist:  # 목록에 있는 모든 소켓에 대해
            print(id)
            print(self.clients)
            print(selected_room_info)
            if id == selected_room_info[0][1] or id == selected_room_info[0][2] or id == selected_room_info[0][3]\
                    or id == selected_room_info[0][4]:
                print(2)
                client = self.clients[i]
                socket = client[0]
                socket.sendall(gr_info.encode())
            i += 1


    def create_room_save_db(self, c_socket):
        roominfo = json.loads(self.recv_signal.decode()[:-6])
        print(roominfo)
        con = pymysql.connect(host='10.10.21.112', user="root3", password="123456789", db='multi_network_server',
                              charset='utf8')
        with con:
            with con.cursor() as cur:
                sql = f"INSERT INTO game_room_list (Room_name,Current_People,Max_people,Game_kind) \
                        values('{roominfo[0]}',1,{int(roominfo[2])},'{roominfo[1]}')"
                cur.execute(sql)
                cur.execute("SELECT * FROM game_room_list order by number desc limit 1")
                created_rm = cur.fetchall()
                print(roominfo)
                print(created_rm)
                sql = f"Insert into game_room_people (Number,user_1) values ({created_rm[0][0]},'{roominfo[3]}')"
                cur.execute(sql)
                cur.execute("select * from game_room_list")
                rows = cur.fetchall()
                cur.execute("select * from game_room_people order by number desc limit 1")
                game_room_info = cur.fetchall()
                con.commit()
                tempdata = json.dumps(rows)
                print(tempdata)
                senddata = tempdata + "100109"
                print(senddata)
                self.final_received_message_gt\
                    = senddata
                self.send_all_clients_gt(c_socket)
                tempdata = json.dumps(game_room_info[0])
                gr_info = tempdata + "100110"
                c_socket.sendall(gr_info.encode())

    def send_room_info(self, c_socket):
        con = pymysql.connect(host='10.10.21.112', user="root3", password="123456789", db='multi_network_server',
                              charset='utf8')
        with con:
            with con.cursor() as cur:
                cur.execute("select * from game_room_list")
                rows = cur.fetchall()
                con.commit()
        tempdata = json.dumps(rows)
        print(tempdata)
        senddata = tempdata + "100109"
        print(senddata)
        c_socket.sendall(senddata.encode())

    def invite_signal_send(self, c_socket):
        self.inviteUsersocket = c_socket
        # selected_userid = self.recv_signal.decode()[:-6]
        invite_room_info = json.loads(self.recv_signal.decode()[:-6])
        selected_userid = invite_room_info[0]
        room_number = invite_room_info[1]
        con = pymysql.connect(host='10.10.21.112', user="root3", password="123456789", db='multi_network_server',
                              charset='utf8')
        with con:
            with con.cursor() as cur:
                cur.execute(f"select * from game_room_list where Number = {room_number}")
                selected_room_info = cur.fetchall()
                tempdata = json.dumps(selected_room_info[0])
                gr_info = tempdata + "100110"  # 방 정보 식별 코드
                i = 0
                for id in self.idlist:
                    if id == selected_userid:
                        tempdata = selected_room_info # [방번호, 제목,현재인원,최대인원,게임종류]
                        senddata = json.dumps(tempdata)
                        self.message = senddata + "846574"
                        self.clients[i][0].sendall(self.message.encode())
                    i += 1

    def login_check(self, c_socket):
        idpw = json.loads(self.recv_signal.decode()[:-6])
        self.idlist.append(idpw[0])
        print(self.idlist)
        try:
            tempdata = json.dumps(self.idlist)
            print(tempdata)
            senddata = tempdata + "985674"
        except:
            print("리시브 메시지 오류발생")
        else:
            self.final_received_message_gt\
                = senddata
            print(self.final_received_message_gt
                  , "파이널리시브")
            self.send_all_clients_gt(c_socket)
            self.send_room_info(c_socket)

    # 데이터를 수신하여 모든 클라이언트에게 전송한다.
    def receive_messages_gt(self, c_socket):
        print(c_socket, "c_socket 프린트")
        try:
            incoming_message = self.recv_signal
            print(incoming_message.decode())
        except:
            print("리시브 메시지 오류발생")
        else:
            self.final_received_message_gt\
                = incoming_message.decode('utf-8')
            print(self.final_received_message_gt
                  , "파이널리시브")
            self.send_all_clients_gt(c_socket)

    # 송신 클라이언트를 제외한 모든 클라이언트에게 메세지 전송
    def send_all_clients_gt(self, senders_socket):
        for client in self.clients:  # 목록에 있는 모든 소켓에 대해
            print(client, "고객")
            socket, (ip, port) = client
            try:
                socket.sendall(self.final_received_message_gt
                               .encode())
            except:  # 연결종료
                self.clients.remove(client)  # 소켓 제거
                print(f"{ip},{port} 연결이 종료 되었습니다.")

    def remove_socket(self, c_socket):

        i = 0
        for client in self.clients:  # 목록에 있는 모든 소켓에 대해
            print(client, "고객")
            socket, (ip, port) = client
            if socket == c_socket:
                self.clients.remove(client)  # 소켓 제거
                self.idlist.remove(self.idlist[i])
                print(f"IP:{ip},Port:{port} 연결이 종료 되었습니다.")
                try:
                    tempdata = json.dumps(self.idlist)
                    senddata = tempdata + "985674"
                except:
                    print("리시브 메시지 오류발생")
                else:
                    self.final_received_message_gt\
                        = senddata
                    self.send_all_clients_gt(c_socket)
                break
            i += 1

if __name__ == "__main__":
    Multi_server = MultiChatServer()
    HOST, PORT = "127.0.0.1", 9048
    with ThreadedTCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()