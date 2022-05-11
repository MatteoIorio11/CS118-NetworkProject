import socket as sk
import time
import os

class Server:
    sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
    @staticmethod
    def open_connection():
        server_address = ('localhost', 10000)
        print('\n\r starting up the server on ip : %s  and port : %s' % server_address)
        sock.bind(server_address)
        return sock

    def get_files():
        print('\n\r Received command : "list files" ')
        list_directories = os.listdir()
        directories = ''.join([ str(directory) for directory in list_directories])
        sock


# Creiamo il socket
    def ciclo(self):
    while True:
        print('\n\r waiting to receive message...')
        data, address = sock.recvfrom(4096)
        print('received %s bytes from %s' % (len(data), address))
        print(data.decode('utf8'))

        if data:
            data1 = 'Programmazione di Reti'
            time.sleep(2)
            sent = sock.sendto(data1.encode(), address)
            print('sent %s bytes back to %s' % (sent, address))



