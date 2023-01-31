import socketserver
import json
from threading import *
import pymysql
from socket import *


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
            self.recv_signal = c_socket.recv(1024)
            print(self.recv_signal.decode())
            if self.recv_signal.decode()[-6:] == "654321":
                self.login_check(c_socket)
            elif self.recv_signal.decode()[-6:] == "123456":
                self.receive_messages(c_socket)
            elif self.recv_signal.decode()[-6:] == "753357":
                self.invite_signal_send(c_socket)
            elif self.recv_signal.decode()[-6:] == "000008":
                self.create_room_save_db(c_socket)
            elif self.recv_signal.decode() == "!@$#@#Socke@$close":
                self.remove_socket(c_socket)
            elif self.recv_signal.decode() == "!@$#@#Socke@$invite":
                self.invite_accept(c_socket)
    def create_room_save_db(self,c_socket):
        roominfo = json.loads(self.recv_signal.decode()[:-6])
        print(roominfo)
        con = pymysql.connect(host='10.10.21.112', user="root3", password="123456789", db='multi_network_server',
                              charset='utf8')
        with con:
            with con.cursor() as cur:
                sql = f"INSERT INTO game_room_list (Room_name,Current_People,Max_people,Game_kind) \
                        values('{roominfo[0]}',1,{int(roominfo[2])},'{roominfo[1]}')"
                cur.execute(sql)
                cur.execute("select * from game_room_list")
                rows = cur.fetchall()
                con.commit()
        tempdata = json.dumps(rows)
        print(tempdata)
        senddata = tempdata + "000009"
        print(senddata)
        self.final_received_message = senddata
        self.send_all_clients(c_socket)
    def send_room_info(self,c_socket):
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
    def invite_accept(self,c_socket):
        pass
        # self.message =
        # for client in self.clients:  # 목록에 있는 모든 소켓에 대해
        #     socket, (ip, port) = client
        #     try:
        #         socket.sendall(self.message.encode())
        #     except:  # 연결종료
        #         self.clients.remove(client)  # 소켓 제거
        #         print(f"{ip},{port} 연결이 종료 되었습니다.")
    def invite_signal_send(self,c_socket):
        self.inviteUsersocket = c_socket
        selected_userid = self.recv_signal.decode()[:-6]
        print(self.idlist)
        i=0
        for client in self.clients:
            socket, (ip, port) = client
            if socket == c_socket :
                self.inviteUserid = self.idlist[i]
                print(self.idlist[i])
            i+=1
        i=0
        for id in self.idlist:
            if id == selected_userid :
                self.invitedUsersocket = self.clients[i][0]
                self.message = self.inviteUserid + "846574"
                self.clients[i][0].sendall(self.message.encode())
            i+=1

    def login_check(self, c_socket):
        idpw= json.loads(self.recv_signal.decode()[:-6])
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

    def remove_socket(self,c_socket):
        i=0
        for client in self.clients:  # 목록에 있는 모든 소켓에 대해
            print(client, "고객")
            socket, (ip, port) = client
            if socket == c_socket :
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
    HOST, PORT = "10.10.21.103", 9048
    # HOST와 PORT를 가지고 ThreadTCPServer를 생성 !
    with ThreadedTCPServer((HOST, PORT), MyTCPHandler) as server:
        # 계속해서 서버 유지
        server.serve_forever()
