import socketserver
import json
from threading import *
import pymysql
from socket import *
from PyQt5.QtWidgets import QMessageBox

class GameHandler(socketserver.BaseRequestHandler):
    # 소켓이 연결되면 실행 되는 handler 메서드
    def handle(self):
        (ip, port) = self.client_address
        client = self.request, (ip, port)
        if client not in Multi_server.clients:
            Multi_server.clients.append(client)
        print(ip, ":", str(port), '가 연결되었습니다.')
        Multi_server.signal_interaction(self.request)

class MyTCPHandler(socketserver.BaseRequestHandler):
    # 소켓이 연결되면 실행 되는 handler 메서드
    def handle(self):
        (ip, port) = self.client_address
        client = self.request, (ip, port)
        if client not in Multi_server.clients:
            Multi_server.clients.append(client)
        print(ip, ":", str(port), '가 연결되었습니다.')
        Multi_server.signal_interaction(self.request)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class MultiChatServer:

    def __init__(self):
        # 여러 클라이언트들을 관리할 리스트를 만들어 준다.
        self.clients = []
        # 마지막으로 받은 메세지가 없는 경우를 대비해서 ""로 지정해줌.
        self.final_received_message = ""  # 최종 수신 메시지
        self.idlist = []

    def signal_interaction(self, c_socket):
        while True:
            try:
                self.recv_signal = c_socket.recv(1024)
            except:
                pass
            else:
                print(self.recv_signal.decode())
                if self.recv_signal.decode()[-6:] == "654321":
                    self.login_check(c_socket)
                elif self.recv_signal.decode()[-6:] == "123456":
                    self.receive_messages(c_socket)
                elif self.recv_signal.decode()[-6:] == "753357":
                    self.invite_signal_send(c_socket)
                elif self.recv_signal.decode()[-6:] == "000008":
                    self.create_room_save_db(c_socket)
                elif self.recv_signal.decode()[-6:] == "000011":
                    self.client_join_room(c_socket)
                elif self.recv_signal.decode()[-6:] == "000013":
                    self.exit_game_room(c_socket)
                elif self.recv_signal.decode()[-6:] == "828282":
                    self.fu_game_play(c_socket)
                elif self.recv_signal.decode() == "!@$#@#Socke@$close":
                    self.remove_socket(c_socket)
                elif self.recv_signal.decode() == "!@$#@#Socke@$invite":
                    self.invite_accept(c_socket)
    def fu_game_play(self,c_socket):
        self.fu_game_play_info = json.loads(self.recv_signal.decode()[:-6])
        print(self.fu_game_play_info)
        if self.fu_game_play_info[0] == "START":
            self.fu_game_start(c_socket)
        elif self.fu_game_play_info[0] == "CHECK" : # game_info = ["CHECK", rm_number, turn, current_people,word]
            self.fu_game_word_check(c_socket)
        elif self.fu_game_play_info[0] == "FAIL" : #game_info = ["FAIL", rm_number, turn, current_people]
            self.fu_game_finish(c_socket)

    def fu_game_finish(self,c_socket):
        room_number = self.fu_game_play_info[1]
        room_turn = self.fu_game_play_info[2]
        room_people_num = self.fu_game_play_info[3]
        word = self.fu_game_play_info[4]
        self.order = int(room_turn) % int(room_people_num)
        tempdata = ["Game_finish", f"<SYSTEM> 잘못된 단어를 입력 하셨습니다.",
                    f"<SYSTEM>{self.order}번 유저의 패배 ! .", word]
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
            tempdata = ["Next_turn", f"<SYSTEM> 다음 차례는 {self.order}번 유저입니다.",
                        f"<SYSTEM>단어는 {word}입니다.", word,new_room_turn]
            senddata = json.dumps(tempdata) + "828282"
        else :
            tempdata = ["Game_finish", f"<SYSTEM> 잘못된 단어를 입력 하셨습니다.",
                        f"<SYSTEM>{self.order}번 유저의 패배 ! .", word]
            senddata = json.dumps(tempdata) + "828282"

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
        print(exit_room_info)
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
                senddata = tempdata + "000009"
                self.final_received_message = senddata
                self.send_all_clients(c_socket)
                if selected_room_info != () :
                    tempdata = json.dumps(selected_room_info[0])
                    gr_info = tempdata + "000010" #방 정보 식별 코드
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
                senddata = tempdata + "000009"
                self.final_received_message = senddata
                self.send_all_clients(c_socket)
                tempdata = json.dumps(selected_room_info[0])
                gr_info = tempdata + "000010" #방 정보 식별 코드
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
                senddata = tempdata + "000009"
                print(senddata)
                self.final_received_message = senddata
                self.send_all_clients(c_socket)
                tempdata = json.dumps(game_room_info[0])
                gr_info = tempdata + "000010"
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
        senddata = tempdata + "000009"
        print(senddata)
        c_socket.sendall(senddata.encode())

    def invite_accept(self, c_socket):
        pass
        # self.message =
        # for client in self.clients:  # 목록에 있는 모든 소켓에 대해
        #     socket, (ip, port) = client
        #     try:
        #         socket.sendall(self.message.encode())
        #     except:  # 연결종료
        #         self.clients.remove(client)  # 소켓 제거
        #         print(f"{ip},{port} 연결이 종료 되었습니다.")

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
                gr_info = tempdata + "000010"  # 방 정보 식별 코드
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
            self.final_received_message = senddata
            print(self.final_received_message, "파이널리시브")
            self.send_all_clients(c_socket)
            self.send_room_info(c_socket)

    # 데이터를 수신하여 모든 클라이언트에게 전송한다.
    def receive_messages(self, c_socket):
        print(c_socket, "c_socket 프린트")
        try:
            incoming_message = self.recv_signal
            print(incoming_message.decode())
        except:
            print("리시브 메시지 오류발생")
        else:
            self.final_received_message = incoming_message.decode('utf-8')
            print(self.final_received_message, "파이널리시브")
            self.send_all_clients(c_socket)

    # 송신 클라이언트를 제외한 모든 클라이언트에게 메세지 전송
    def send_all_clients(self, senders_socket):
        for client in self.clients:  # 목록에 있는 모든 소켓에 대해
            print(client, "고객")
            socket, (ip, port) = client
            try:
                socket.sendall(self.final_received_message.encode())
            except:  # 연결종료
                self.clients.remove(client)  # 소켓 제거
                print(f"{ip},{port} 연결이 종료 되었습니다.")

    def remove_socket(self, c_socket):
        con = pymysql.connect(host='10.10.21.112', user="root3", password="123456789", db='multi_network_server',
                              charset='utf8')

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
                    self.final_received_message = senddata
                    self.send_all_clients(c_socket)
                break
            i += 1


if __name__ == "__main__":
    # MultiChatServer 클래스의 객체를 생성 !
    Multi_server = MultiChatServer()
    # 호스트와 포트를 localhost = 127.0.0.1 / 55000으로 지정해준다.
    HOST, PORT = "127.0.0.1", 9048
    # HOST와 PORT를 가지고 ThreadTCPServer를 생성 !
    with ThreadedTCPServer((HOST, PORT), MyTCPHandler) as server:
        # 계속해서 서버 유지
        server.serve_forever()
    print(456)