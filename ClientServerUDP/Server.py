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
        metadata = ''.join([ str(directory).join("\n") for directory in list_directories if os.path.isfile(directory)])
        print('\n\r Sending all the files in the Directory...')
        self.error_flag = 0
        return metadata

    def download(self, file):
        if file in os.listdir():
            print('\n\r Sending the file ' % file % ' to the destination')
            input_file = open('file', 'rb')
            metadata = pickle.load(input_file)
            input_file.close()
            size = os.path.getsize(file)
            self.error_flag = 0
            return {metadata, size}
        else:
            self.error_flag = 1

    def upload(self, file):
        if file in os.listdir():
            print('\n\r Upload ' % file % ' in the current directory')
            output_file = open('file', 'wb')
            self.error_flag = 0
        else:
            self.error_flag = 1

    def send_package(self, destination, data):
        self.socket.sendto(data.encode(), destination)
        time.sleep(1)

    def send_header(self, destination, operation, file_name, size):
        header = {"operation" : operation,
                  "file_name" : file_name,
                  "status" : False if self.error_flag == 1 else True,
                  "size" : size}
        self.send_package(destination, json.dump(header))

    def send_metadata(self, metadata, destination):
        metadata = {"metadata": metadata}
        self.send_package(destination, json.dump(metadata))

    def launch_server(self):
        while True:
            message, client = self.socket.recvfrom(4096)
            header = json.loads(message.decode())
            operation = "operation" in header
            file_name = "file_name" in header

            if operation == Operation.GET_FILES.value:
                metadata = self.get_files(client)
                self.send_header(client, operation, "", 0)
                message, client = self.socket.recvfrom(4090)
                status_header = json.loads(message.decode())
                status = "operation" in status_header
                self.send_metadata(metadata, client) if status == Operation.ACK.value else break
            elif operation == Operation.DOWNLOAD.value:
                metadata, size = self.download(file_name)
                self.send_header(client, operation, file_name, size)
                status_header = json.loads(message.decode())
                status = "operation" in status_header
                self.send_metadata(metadata, client) if status == Operation.ACK.value else break
            elif operation == Operation.UPLOAD.value:
                metadata, size = self.upload(file_name)
                self.send_header(client, operation, file_name, size)



