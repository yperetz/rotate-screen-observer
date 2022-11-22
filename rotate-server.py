import socket
import subprocess
from _thread import *
from threading import Lock
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

IP = os.getenv('MY_IP')
PORT = os.getenv('MY_PORT')


class RotateServer:
    pos = {"1": "normal", "2": "left", "3": "right", "4": "inverted", }

    def __init__(self, host=IP, address=int(PORT), buffsize=1024):
        _port = address
        _buffsize = buffsize
        num_threads = 0
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._all_conns = {}
        self._mutex = Lock()

        try:
            s.bind((host, _port))
        except socket.error as e:
            print(e)
        print("Server is listening")
        s.listen(5)
        while True:
            conn, addr = s.accept()
            print(f'[Server-print] Connected to {addr[0]}: {str(addr[1])}')
            num_threads += 1
            start_new_thread(self._multi_thread_client,
                             (conn, addr, num_threads))
            print(f"num conections: {num_threads}")
        s.close()

    def _multi_thread_client(self, conn: socket.socket, addr, tid):
        conn.send(str.encode('server is working'))
        while True:
            data = conn.recv(2048)
            decoded = data.decode('utf-8')
            response = '[Server] ' + decoded
            if not data:
                continue
            if decoded == 's':
                self._attach(conn, addr, tid)
                conn.sendall(str.encode(
                    f"{addr[0]}:{addr[1]} is now subscribed"))
            elif decoded == 'u':
                self._detach(tid)
                conn.sendall(str.encode(
                    f"{addr[0]}:{addr[1]} is now Unsubscribed"))
            else:
                self._rotate(decoded)

            conn.sendall(str.encode(response))
        conn.close()

    def _attach(self, conn, addr, tid):
        self._mutex.acquire()
        self._all_conns[tid] = (conn, addr)
        self._mutex.release()

    def _detach(self, tid):
        self._mutex.acquire()
        self._all_conns.pop(tid, 0)  # adding def value for no error
        self._mutex.release()

    def _rotate(self, decoded):
        if decoded not in self.pos.keys():
            return
        res = subprocess.run(
            ['xrandr', '--output', 'DP-1', '--rotate',
             self.pos[decoded]], capture_output=True)
        print(res.stdout)
        self._notify(self.pos[decoded])

    def _notify(self, position):
        self._mutex.acquire()
        for c, addr in self._all_conns.values():
            c.sendall(str.encode(f"Position changed: {position}"))
        self._mutex.release()


if __name__ == '__main__':
    r = RotateServer()
