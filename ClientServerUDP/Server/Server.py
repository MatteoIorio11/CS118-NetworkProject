import hashlib

from HeaderBuilder import HeaderBuilder
from Operation import Operation
import socket as sk
import time
import json
import os
import yaml
import base64
import threading
import math


# Server Class.
# This class represent the Server. The Server has to manage the Client's request and handle It
# with the right operations. For example if Client request Operation.GET_FILES the Server has to
# send to the Client all the files in the directory of the Server.
# This class has Its own socket composed by Port and Address ( in general the Address is the 'localhost' ),
# after that all the Server's methods are the specific operations that the Server can handle.
# This Server use a specific format for the header datagram:
#
#
#   |----------------------------------------|
#   | operation : Operation.XXX.value        |
#   | file_name : beautiful_file.txt or  ""  |
#   | status    : True Or False              |
#   | checksum  : aaa                        |
#   | size      : size of the file_name      |
#   | metadata  : file content or ""         |
#   |----------------------------------------|
#
#
# * The "operation" stands for what type of Operation the Client has request < SEE Operation.py >.
# * The "file name" stands for the specific name of the file, this field can be empty if the operation requested does
#   not involve a file ( like the Operation.GET_FILES does not involve any type of file ).
# * The "status" is a field where the Server can notify the Client of an error, for example if a Client request
#   Operation.Download operation and the Client send a file that is not contained in the Server's path, the
#   status field will be False, because the file requested does not exist in the Server's path.
# * The "size" stands for the "file_name"'s size, this field can be < 0 > if the Client's Operation
#   does not interest a file ( for example Operation.GET_FILES), but if the Operation is Operation.UPLOAD in this field
#   the Server will see the size of the file.
# * The "metadata" is where all the file's content is put. If the Client request Operation.DOWNLOAD, in this field the
#   Server will see how much is big the metadata field.

class Server:
    port = 0                                    # The port where the Server is listening
    address = ''                                # The address of the Server
    buffer_size = 0                             # How much is big the buffer for reading files
    time_to_sleep = 0                           # How much time the Server has to sleep before to send another package
    socket = 0                                  # Server's socket
    path = os.path.join(os.getcwd(), 'Server')  #
    menu = " Hi, This is the UDP Server. Here are the possible operations that you can do: \n" \
           " 1) Get the list of all my files \n" \
           " 2) Download a file from my list files \n" \
           " 3) Upload your file in my directory \n" \
           " 4) EXIT"

    # Define the constructor of the Server
    def __init__(self):
        file = os.path.join(self.path, 'config.yaml')  # path of the configuration file
        with open(file, 'r') as file:
            dictionary = yaml.load(file, Loader=yaml.Loader)
        self.address = str(dictionary['address'])
        self.port = dictionary['port']
        self.buffer_size = dictionary['buffer_size']
        self.time_to_sleep = dictionary['time_to_sleep']
        self.path = os.path.join(self.path, dictionary['path'])
        self.socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.socket.settimeout(dictionary['timeout']*1000)

    # Argument : self
    # This method set the server address -> set the IP and the PORT and then the creation of the Server's socket
    def start_server(self):
        server_address = (self.address, self.port)
        print('\n\r starting up the server on ip : %s  and port : %s' % server_address)
        self.socket.bind(server_address)
        self.launch_server()  # Launch the Server's main application

    # Argument : self
    # Argument : client
    # Return : All the files in the current directory
    # This method get all the files in the current directory of the server
    def get_files(self, client):
        print('\n\r Received command : "list files" ')
        list_directories = os.listdir(self.path)
        metadata = ''.join([(str(directory)+"\n") for directory in list_directories])
        md5_hash = hashlib.md5()
        md5_hash.update(metadata.encode())
        header = HeaderBuilder.build_header(Operation.GET_FILES.value, True, md5_hash.hexdigest(),
                                            "", 0, metadata.encode())
        self.send_package(client, header)
        print('\n\r Sending all the files in the Directory...')
        return metadata

    # Argument : file
    # Argument : client
    # This method read multiple chunks of the selected file, after every chunk
    # the Server send It to the Client. The chunk size is 8192 bytes
    def download(self, file, client):
        if file in os.listdir(self.path):
            print('Sending the file ' + str(file) + ' to the destination.\n')
            file_size = math.ceil(os.path.getsize(os.path.join(self.path, file))/self.buffer_size)
            header = HeaderBuilder.build_header(Operation.ACK.value, True, hash('ACK'), "", 0, str(file_size).encode())
            self.send_package(client, header)
            time.sleep(self.time_to_sleep)
            md5_hash = hashlib.md5()
            with open(os.path.join(self.path, file), 'rb') as handle:
                byte = handle.read(self.buffer_size)   # Read a buffer size
                status_download = 1
                md5_hash.update(byte)
                while byte:
                    print(status_download)
                    header = HeaderBuilder.build_header(Operation.SENDING_FILE.value, True,
                                                        md5_hash.hexdigest(),
                                                        file, self.buffer_size, byte)
                    percentage = int((status_download*100)/file_size)
                    self.send_package(client, header)
                    print("Percentage of sent packages : " + str(percentage) + "\n")
                    time.sleep(self.time_to_sleep)
                    byte = handle.read(self.buffer_size)   # Read a buffer size
                    status_download = status_download + 1
                    md5_hash.update(byte)
            md5_hash.update('ACK'.encode())
            header = HeaderBuilder.build_header(Operation.END_FILE.value, True, md5_hash.hexdigest(),
                                                "", 0, "ACK".encode())  # Send the bytes read to the Client
            print('\n\r All packages have been sent to the client.')
            self.send_package(client, header)
        else:
            header = HeaderBuilder.build_header(Operation.ERROR.value, False, hash("Error"),
                                                "", 0, "The input file does not exist in the directory".encode())
            self.send_package(client, header)

    # Argument : self
    # Argument : file
    # Argument : metadata_files
    # Return
    # This method write the metadata in input inside the new file named : file.
    def upload(self, file, message, client):
        print("The Server is ready to receive the file from the Client.\n")
        buffer_reader_size = 16_384
        file_name = message['file_name']
        if file_name in os.listdir(self.path):
            print("AAAAAA")
            file_name = os.path.splitext(file_name)[0] + "(copy)" + os.path.splitext(file_name)[1]
        tot_packs = int(base64.b64decode(message['metadata']).decode())   # tot packs that I should receive
        cont_packs = 0
        md5 = hashlib.md5()
        md5.update("ACK".encode())
        header = HeaderBuilder.build_header(Operation.ACK.value, True, md5.hexdigest(), "", 0, "ACK".encode())
        self.send_package(client, header)
        md5 = hashlib.md5()
        with open(os.path.join(self.path, file), 'wb') as f:
            while True:
                data = self.socket.recv(buffer_reader_size)
                data_json = json.loads(data.decode())
                checksum = data_json['checksum']
                md5.update(base64.b64decode(data_json['metadata']))
                res = md5.hexdigest()
                
                if not data_json['status'] or checksum != res :
                    raise Exception(base64.b64decode(data_json['metadata']))
                if data_json['operation'] == Operation.END_FILE.value:
                    break
                else:
                    cont_packs += 1
                file = base64.b64decode(data_json['metadata'])
                f.write(file)
        ack = HeaderBuilder.build_header(Operation.ACK.value, True, hash(''), "", 0, "".encode())
        if tot_packs != cont_packs :
            print("Not all packages have been arrived")
            ack = HeaderBuilder.build_header(Operation.ACK.value, False, hash(''), "", 0, "".encode())
        else:
            print('\n\r All packages have been saved, the File is now available in the path : ' +
                  os.path.join(self.path, str(file_name)))
        self.send_package(client, ack)

    # Argument : self
    # Argument : destination
    # Argument : data
    # This method send a UDP package
    def send_package(self, destination, data):
        self.socket.sendto(data.encode(), destination)
        time.sleep(self.time_to_sleep)

    def send_menu(self, destination):
        md5_hash = hashlib.md5()
        md5_hash.update(self.menu.encode())
        header = HeaderBuilder.build_header(Operation.ACK.value, True, md5_hash.hexdigest(), "", 0, self.menu.encode())
        self.send_package(destination, header)

    # Argument : self
    # Main method of the Server. Here is where all the Client's request are managed
    # For every message received the served send an Operation.ACK to the Client.
    def launch_server(self):
        while True:
            # The server wait for a message receive from another Host
            message, client = self.socket.recvfrom(4096)
            header = json.loads(message.decode())  # Decoding of the file and parsing It in to the JSON format
            operation = header['operation']  # Get the Operations requested
            file_name = header['file_name']  # Get the file name
            if operation == Operation.OPEN_CONNECTION.value:
                self.send_menu(client)

            # First Operations : GET FILES
            elif operation == Operation.GET_FILES.value:
                self.get_files(client)

            elif operation == Operation.DOWNLOAD.value:
                t = threading.Thread(target=self.download, args=(file_name,client))
                t.start() 

            elif operation == Operation.UPLOAD.value:
                self.upload(file_name, header, client)

            elif operation == Operation.EXIT.value:
                self.socket.close()
                print("The Server is closing...")
                return
