import socket
import threading
from threading import Lock
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
IP = os.getenv('MY_IP')
PORT = os.getenv('MY_PORT')
mutex = Lock()


def listen_thread(s):
    while True:
        res = s.recv(1024)
        print(res.decode('utf-8'))


def start_client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, int(PORT)))
    s.sendall(b"hi all")
    data = s.recv(1024)
    print('Received', repr(data))
    t = threading.Thread(target=listen_thread, args=(s,))
    t.daemon = True
    t.start()

    while True:
        try:
            inp = input("enter number")
            s.sendall(bytes(inp, encoding='utf8'))
        except Exception as e:
            print(f"exception: {e}")
            s.close()


start_client()
