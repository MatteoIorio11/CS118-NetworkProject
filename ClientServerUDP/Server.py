import socket
import time
import os
import pickle

class Server:
    port = 0
    address = 0
    socket = 0
    def __init__(self, port , address):
        self.port = port
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def open_connection(self):
        server_address = (self.addres, self.port)
        print('\n\r starting up the server on ip : %s  and port : %s' % server_address)
        self.socket.bind(server_address)

    def get_files(self, destination):
        print('\n\r Received command : "list files" ')
        list_directories = os.listdir()
        directories = ''.join([ str(directory) for directory in list_directories if os.path.isfile(directory)])
        print('\n\r Sending all the files in the Directory...')
        self.socket.sendto(directories.encode(), destination)

    def download(self, file, destination):
        if file in os.listdir():
            input_file = open('file', 'rb')
            file_content = pickle.load(input_file)
            input_file.close()

        else:
            error_message = '\n\r Error : The selected file does not exist in the path directory.'
            self.socket.sendto(error_message.encode(), destination)

    def upload(self, file, destination):
        if file in os.listdir():
            error_message = '\n\r Error : The selected file does not exist in the path directory.'
            self.socket.sendto(error_message.encode(), destination)
        else:
            print('\n\r Upload the sended file')
            output_file = open('file', 'wb')




