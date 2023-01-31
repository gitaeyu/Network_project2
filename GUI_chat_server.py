#threading 모듈을 이용한  TCP 멀티 채팅서버 프로그램

from socket import *
from threading import*
import pymysql as p
class MultiChatServer:

    #소켓을 생성하고 연결되면 accept_client() 호출

    def __init__(self):
        self.clients = []
        self.final_received_message = "" #최종 수신 메시지
        self.s_sock = socket(AF_INET, SOCK_STREAM)
        self.ip = '127.0.0.1'
        self.port = 56800
        self.s_sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.s_sock.bind((self.ip,self.port))
        print("클라이언트 대기중...")
        self.s_sock.listen(100)
        thread1 = Thread(target=self.signal_interaction)
        thread1.start()
        thread2 = Thread(target=self.signal_interaction)
        thread2.start()
    #연결 클라이언트 소켓을 목록에 추가하고 스레드를 생성하여 데이터를 수신한다.
    def signal_interaction(self):
        while True:
            client = c_socket, (ip,port) = self.s_sock.accept()
            print(c_socket,(ip,port))
            if client not in self.clients :
                self.clients.append(client) #접속된 소켓을 목록에 추가
            print(ip,":",str(port),'가 연결되었습니다.')
            self.recv_signal = c_socket.recv(256)
            print(self.recv_signal.decode()[:-6])
            if self.recv_signal.decode()[-6:] == "654321":
                self.login_check()

    def login_check(self):
        print("423234")
    #데이터를 수신하여 모든 클라이언트에게 전송한다.
    def receive_messages(self,c_socket):
        try:
            incoming_message = c_socket.recv(256)
        except:
            pass
        else:
            self.final_received_message = incoming_message.decode('utf-8')
            self.send_all_clients(c_socket)
    #송신 클라이언트를 제외한 모든 클라이언트에게 메세지 전송
    def send_all_clients(self, senders_socket):
        for client in self.clients: #목록에 있는 모든 소켓에 대해
            print(client,"클라이언트 프린트")
            socket, (ip,port) = client
            if socket is not senders_socket: #송신 클라이언트는 제외
                try:
                    socket.sendall("@!#$@chatting".encode())
                    socket.sendall(self.final_received_message.encode())
                except: #연결종료
                    self.clients.remove(client) #소켓 제거
                    print(f"{ip},{port} 연결이 종료 되었습니다.")

if __name__=="__main__" :
    MultiChatServer()