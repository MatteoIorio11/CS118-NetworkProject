import hashlib
import signal
import socket

from HeaderFactory import HeaderFactory
from FileNameFactory import FileNameFactory
from Operation import Operation
from Utils import Util
import socket as sk
import time
import json
import os
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
#   | checksum  : f1e069787e...              |
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
# * The "checksum" field is used for the integrity of our messages, this field has the hashlib.md5().hexdigest()
#   of the metadata. With this field we can have the integrity.
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
    timeout = 0
    path = os.path.join(os.getcwd(), 'Server')  #
    menu = " Hi, This is the UDP Server. Here are the possible operations that you can do: \n" \
           " 1) Get the list of all my files \n" \
           " 2) Download a file from my list files \n" \
           " 3) Upload your file in my directory \n" \
           " 4) EXIT"

    # Define the constructor of the Server
    def __init__(self):
        file = os.path.join(self.path, 'config.json')  # path of the configuration file
        with open(file, 'r') as openfile:
            dictionary = json.load(openfile)
        self.address = str(dictionary['address'])
        self.port = dictionary['port']
        self.buffer_size = dictionary['buffer_size']
        self.time_to_sleep = dictionary['time_to_sleep']
        self.path = os.path.join(self.path, dictionary['path'])
        self.socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.timeout = dictionary['timeout']
        signal.signal(signal.SIGINT, self.close_socket)

    def close_socket(self, signum, frame):
        print("The Server is closing...\n")
        self.socket.close()
        exit(0)

    # Argument : self
    # This method set the server address -> set the IP and the PORT and then the creation of the Server's socket
    def start_server(self):
        server_address = (self.address, self.port)
        print('--- starting up the server on ip : %s  and port : %s ---' % server_address)
        self.socket.bind(server_address)
        self.launch_server()  # Launch the Server's main application

    # Argument : self
    # Argument : client
    # Return : All the files in the current directory
    # This method get all the files in the current directory of the server
    def get_files(self, client):
        print(' -> Received command : "list files" ')
        list_directories = os.listdir(self.path)
        metadata = ''.join([(str(directory)+"\n") for directory in list_directories])
        header = HeaderFactory.build_operation_header_wchecksum(Operation.GET_FILES.value,
                                                                Util.get_hash_with_metadata(metadata.encode()),
                                                                metadata.encode())
        self.send_package(client, header)
        print(' -> Sending all the files in the Directory...')
        return metadata

    # Argument : file
    # Argument : client
    # This method read multiple chunks of the selected file, after every chunk
    # the Server send It to the Client. The chunk size is 8192 bytes
    def download(self, file, client):
        try:
            self.socket.settimeout(self.timeout)
            if file in os.listdir(self.path):
                print(' -> Sending the file ' + str(file) + ' to the destination.')
                # Creation of the ACK header
                file_size = math.ceil(os.path.getsize(os.path.join(self.path, file))/self.buffer_size)
                header = HeaderFactory.build_ack_header_wchecksum(Util.get_hash_with_metadata(str(file_size).encode()),
                                                                  str(file_size).encode())
                self.send_package(client, header)
                time.sleep(self.time_to_sleep)
                md5_hash = hashlib.md5()
                with open(os.path.join(self.path, file), 'rb') as handle:
                    byte = handle.read(self.buffer_size)   # Read a buffer size
                    status_download = 1
                    md5_hash = Util.update_md5(md5_hash, byte) # Creation of the checksum
                    while byte:
                        percentage = Util.get_percentage(status_download, file_size)
                        print("{:03d}".format(percentage), "%", end='\r')
                        header = HeaderFactory.build_operation_header_wsize(Operation.SENDING_FILE.value, file,
                                                                            Util.get_digest(md5_hash),
                                                                            self.buffer_size, byte)
                        self.send_package(client, header) # Sending to the Client what the Server read
                        time.sleep(self.time_to_sleep)
                        byte = handle.read(self.buffer_size)   # Read a buffer size
                        status_download = status_download + 1
                        md5_hash = Util.update_md5(md5_hash, byte)
                md5_hash = Util.update_md5(md5_hash, 'ACK'.encode())
                # Total read of the file
                header = HeaderFactory.build_operation_header_wchecksum(Operation.END_FILE.value,
                                                                        Util.get_digest(md5_hash),
                                                                        'ACK'.encode())
                # Send the bytes read to the Client
                print(' -> All packages have been sent to the client.')
                self.send_package(client, header)
            else:
                header = HeaderFactory.build_error_header(
                                        Util.get_hash_with_metadata(
                                            "The input file does not exist in the directory".encode()),
                                        "The input file does not exist in the directory".encode())
                self.send_package(client, header)
            self.socket.settimeout(None)
        except sk.timeout as e:
            # The timeout is over
            self.socket.settimeout(None)
            print(" -> The timeout is over. Something went wrong...\n")

    # Argument : self
    # Argument : file
    # Argument : metadata_files
    # Return
    # This method write the metadata in input inside the new file named : file.
    def upload(self, file, message, client):
        tries = 1
        try:
            self.socket.settimeout(self.timeout)
            while True:
                error = False
                print(" -> The Server is ready to receive the file from the Client.")
                buffer_reader_size = 16_384
                file_name = FileNameFactory.get_file_name(file, message['file_name'], self.path)
                tot_packs = int(base64.b64decode(message['metadata']).decode())   # tot packs that I should receive
                cont_packs = 0
                header = HeaderFactory.build_ack_header()
                self.send_package(client, header)
                md5 = hashlib.md5()
                with open(os.path.join(self.path, file_name), 'wb') as f:
                    while True:
                        data = self.socket.recv(buffer_reader_size)
                        data_json = json.loads(data.decode())
                        checksum = data_json['checksum']
                        md5 = Util.update_md5(md5, base64.b64decode(data_json['metadata']))
                        res = Util.get_digest(md5)
                        if not data_json['status']:
                            print(" -> The status is false. Something went wrong. Exit from the upload")
                            error = True
                            break
                        elif checksum != res:
                            print("The checksum is no correct..")
                            tries = tries + 1
                            error = True
                            ack = HeaderFactory.build_error_header(Util.get_hash_with_metadata(
                                                                   "Not all packages have been arrived".encode()),
                                                                   "Not all packages have been arrived".encode())
                            self.send_package(client, ack)
                            break
                        if data_json['operation'] == Operation.END_FILE.value:
                            break
                        else:
                            cont_packs += 1
                        file = base64.b64decode(data_json['metadata'])
                        f.write(file)
                if not error:
                    break
                else:
                    os.remove(os.path.join(self.path, file_name))
                if tries > 5:
                    self.socket.settimeout(None)
                    print(" -> Tried Five times. EXIT THE OPERATION...")
                    return
            ack = HeaderFactory.build_ack_header()
            if tot_packs != cont_packs:
                print(" -> Not all packages have been arrived")
                os.remove(os.path.join(self.path, file_name))
                ack = HeaderFactory.build_error_header(Util.get_hash_with_metadata(
                                                       "Not all packages have been arrived".encode()),
                                                       "Not all packages have been arrived".encode())
            else:
                print(' -> All packages have been saved, the File is now available in the path : ' +
                      os.path.join(self.path, str(file_name)))
            self.send_package(client, ack)
            self.socket.settimeout(None)
        except sk.timeout as e:
            if file_name in os.listdir(self.path):
                os.remove(os.path.join(self.path, file_name))
            # The timeout is over
            self.socket.settimeout(None)
            print(" -> The timeout is over. Something went wrong.")

    # Argument : self
    # Argument : destination
    # Argument : data
    # This method send a UDP package
    def send_package(self, destination, data):
        self.socket.sendto(data.encode(), destination)
        time.sleep(self.time_to_sleep)

    def send_menu(self, destination):
        header = HeaderFactory.build_operation_header_wchecksum(Operation.ACK.value,
                                                                Util.get_hash_with_metadata(self.menu.encode()),
                                                                self.menu.encode())
        # self.send_package(destination, header)

    # Argument : self
    # Main method of the Server. Here is where all the Client's request are managed
    # For every message received the served send an Operation.ACK to the Client.
    def launch_server(self):
        while True:
            # The server wait for a message receive from another Host
            self.socket.settimeout(None)
            message, client = self.socket.recvfrom(4096)
            header = json.loads(message.decode())  # Decoding of the file and parsing It in to the JSON format
            operation = header['operation']  # Get the Operations requested
            file_name = header['file_name']  # Get the file name
            if operation == Operation.OPEN_CONNECTION.value:
                self.send_menu(client)

            # First Operations : GET FILES
            elif operation == Operation.GET_FILES.value:
                print("Command : FILES")
                self.get_files(client)

            elif operation == Operation.DOWNLOAD.value:
                print("Command : DOWNLOAD")
                t = threading.Thread(target=self.download, args=(file_name, client))
                t.start() 

            elif operation == Operation.UPLOAD.value:
                print("Command : UPLOAD")
                self.upload(file_name, header, client)
