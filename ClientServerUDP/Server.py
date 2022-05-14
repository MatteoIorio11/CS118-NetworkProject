import socket as sk
import time
import json
from Operation import Operation
import os
import pickle


class Server:
    port = 0
    address = ''
    socket = 0
    error_flag = 0

    def __init__(self, port , address):
        self.port = port
        self.address = str(address)
        self.socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

    def start_server(self):
        server_address = ('localhost', 20000)
        print('\n\r starting up the server on ip : %s  and port : %s' % server_address)
        self.socket.bind(server_address)
        self.launch_server()

    def get_files(self, destination):
        print('\n\r Received command : "list files" ')
        list_directories = os.listdir()
        metadata = ''.join([ str(directory) for directory in list_directories if os.path.isfile(directory)])
        print('\n\r Sending all the files in the Directory...')
        self.error_flag = 0
        return metadata

    def download(self, file, destination):
        if file in os.listdir():
            print('\n\r Sending the file ' % file % ' to the destination')
            input_file = open('file', 'rb')
            file_content = pickle.load(input_file)
            input_file.close()
            self.error_flag = 0
        else:
            self.error_flag = 1

    def upload(self, file, destination):
        if file in os.listdir():
            print('\n\r Upload ' % file % ' in the current directory')
            output_file = open('file', 'wb')
            self.error_flag = 0
        else:
            self.error_flag = 1

    def send_package(self, destination, data):
        self.socket.sendto(data.encode(), destination)
        time.sleep(1)

    def send(self, metadata, destination, operation, file_name):
        header = {"operation" : operation,
                  "file_name" : file_name,
                  "status" : False if self.error_flag == 1 else True}
        self.send_package(destination, json.dumps(header))
        message = {"metadata": metadata}
        self.send_package(destination, json.dumps(message))

    def launch_server(self):
        while True:
            message, client = self.socket.recvfrom(4096)
            #header = json.load(message.decode('utf8'))
            operation = 1
            if operation == Operation.GET_FILES.value:
                metadata = self.get_files(client)
                self.send(metadata, client, operation, "")



