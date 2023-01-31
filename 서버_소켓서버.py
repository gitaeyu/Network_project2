import socketserver
import pymysql
import time

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
        self.clients = []
        self.final_received_message = "" #최종 수신 메시지
        self.room_select = "chat_all"


    #데이터를 수신하여 모든 클라이언트에게 전송한다.
    def receive_messages(self,c_socket):
        print(c_socket, "c_socket 프린트")
        while True:
            try:
                incoming_message = c_socket.recv(512)
                if not incoming_message : #연결이 종료됨
                    break
            except:
                continue
            else:
                self.final_received_message = incoming_message.decode('utf-8')
                # DB에 수신 메시지 넣어줌
                if self.final_received_message[-3:] != '001' and self.final_received_message[-3:] != '002' and self.final_received_message[-3:] != '003' and self.final_received_message[-3:] != '004':
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='multi_network_server', charset='utf8')
                    with con:
                        with con.cursor() as cur:
                            sql = f"INSERT INTO {self.room_select} values('{self.final_received_message}')"
                            cur.execute(sql)
                            con.commit()
                    ###################################################### Data base 접속 end
                self.send_all_clients(c_socket)
        c_socket.close()
    #송신 클라이언트를 제외한 모든 클라이언트에게 메세지 전송
    def send_all_clients(self, senders_socket):
        for client in self.clients: #목록에 있는 모든 소켓에 대해
            print(client)
            socket, (ip,port) = client
            if socket is not senders_socket: #송신 클라이언트는 제외
                try:
                    print(self.final_received_message[-3:])
                    print("abc")
                    if self.final_received_message[-3:] != '001' and self.final_received_message[-3:] != '002' and self.final_received_message[-3:] != '003' and self.final_received_message[-3:] != '004':
                        print("def")
                        socket.sendall((self.final_received_message+'000').encode())
                except: #연결종료
                    self.clients.remove(client) #소켓 제거
                    print(f"{ip},{port} 연결이 종료 되었습니다.")
            else:
                if self.final_received_message[-3:] == '001':               # 채팅창 불러오기 code
                    # print(self.final_received_message)
                    # print(self.final_received_message[:-3])
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='multi_network_server', charset='utf8')
                    with con:
                        with con.cursor() as cur:
                            sql = f"SELECT * FROM {self.final_received_message[:-3]}"
                            cur.execute(sql)
                            rows = cur.fetchall()
                    ##################################################### Data base 접속 end
                    for x in rows:
                        # print(str(x[0]))
                        time.sleep(0.0001)
                        socket.sendall((str(x[0]) + '001').encode())
                elif self.final_received_message[-3:] == '002':             # 채팅방 목록 불러오기 code
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='multi_network_server', charset='utf8')
                    with con:
                        with con.cursor() as cur:
                            sql = f"SHOW TABLES LIKE 'chat%'"
                            cur.execute(sql)
                            rows = cur.fetchall()
                    ##################################################### Data base 접속 end
                    for x in rows:
                        # print(str(x[0]))
                        time.sleep(0.0001)
                        socket.sendall((str(x[0]) + "002").encode())
                elif self.final_received_message[-3:] == '003':  # 채팅방 목록 불러오기 code
                    print(self.final_received_message)
                    print(self.final_received_message[:-3])
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str,db='multi_network_server', charset='utf8')
                    with con:
                        with con.cursor() as cur:
                            sql = f"CREATE TABLE {self.final_received_message[:-3]}(text TEXT) ENGINE= InnoDB CHARSET=utf8mb4;"
                            cur.execute(sql)
                            con.commit()
                    ###################################################### Data base 접속 end
                elif self.final_received_message[-3:] == '004':  # 채팅방 이름 서버에 전달하는 code
                    self.room_select = self.final_received_message[:-3]



if __name__ == "__main__":
    Multi_server = MultiChatServer()
    HOST, PORT = "localhost", 55000
    with ThreadedTCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()