import socket as sk
import time
import json
from Operation import Operation
import os


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
#   | operation : Operations.XXX.value       |
#   | file_name : beautiful_file.txt or  ""  |
#   | status    : True Or False              |
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
    port = 0        # The port where the Server is listening
    address = ''    # The address of the Server
    socket = 0      # Server's socket
    error_flag = 0  # Flag used in order to notify the client of an internal error

    # Define the constructor of the Server
    def __init__(self, port, address):
        self.port = port
        self.address = str(address)
        self.socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

    # Argument : self
    # This method set the server address -> set the IP and the PORT and then the creation of the Server's socket
    def start_server(self):
        server_address = ('localhost', 20000)
        print('\n\r starting up the server on ip : %s  and port : %s' % server_address)
        self.socket.bind(server_address)
        self.launch_server()  # Launch the Server's main application

    # Argument : self
    # Return : All the files in the current directory
    # This method get all the files in the current directory of the server
    def get_files(self):
        print('\n\r Received command : "list files" ')
        list_directories = os.listdir()
        metadata = ''.join([(str(directory)+"\n") for directory in list_directories if os.path.isfile(directory)])
        print('\n\r Sending all the files in the Directory...')
        self.error_flag = 0  # No errors, the flag is false
        return metadata

    # Argument : file
    # Argument : client
    # This method read multiple chunks of the selected file, after every chunk
    # the Server send It to the Client. The chunk size is 8192 bytes
    def download(self, file, client):
        if file in os.listdir():
            print('\n\r Sending the file ' % file % ' to the destination')
            buffer_size = 8192
            with open(file, 'rb') as handle:
                for _ in handle:
                    byte = handle.read(buffer_size)   # Read a buffer size
                    self.send_metadata(byte, client)  # Send the bytes read to the Client
                    time.sleep(0.001)
            self.error_flag = 0  # No errors the file is in the current directory of the Server
        else:
            self.error_flag = 1  # The selected file does not exist in the current directory of the Server

    # Argument : self
    # Argument : file
    # Argument : metadata_files
    # Return
    # This method write the metadata in input inside the new file named : file.
    def upload(self, file, metadata_files):
        if file in os.listdir():

            self.error_flag = 0
        else:
            self.error_flag = 1

    # Argument : self
    # Argument : destination
    # Argument : data
    # This method send a UDP package
    def send_package(self, destination, data):
        self.socket.sendto(data.encode(), destination)
        time.sleep(1)

    # Argument : self
    # Argument : destination    < The Client >
    # Argument : operation      < Which Operations is sent (see Operation.py) >
    # Argument : file:name      < What is the name of the requested\sent file >
    # Argument : Size           < The size of the file_name >
    # This method create the header file and then the Server send it to the client
    def send_header(self, destination, operation, file_name, size):
        header = {
                "operation": operation,
                "file_name": file_name,
                "status": False if self.error_flag == 1 else True,
                "size": size
                }
        self.send_package(destination, json.dumps(header))

    # Argument : self
    # Argument : metadata
    # Argument : destination
    # This method create the metadata header and the Server send it to the client
    # Useless does not make any sens send a metadata package without the header file
    def send_metadata(self, metadata, destination):
        metadata = {"metadata": metadata}
        self.send_package(destination, json.dumps(metadata))

    def get_file_size(self, file):
        if file in os.listdir():
            return os.path.getsize(file)
        else:
            self.error_flag = 1
            return -1

    # Argument : self
    # Main method of the Server. Here is where all the Client's request are managed
    # For every message received the served send an Operation.ACK to the Client.
    def launch_server(self):
        while True:
            # The server wait for a message receive from another Host
            message, client = self.socket.recvfrom(4096)
            header = json.loads(message.decode())  # Decoding of the file and parsing It in to the JSON format
            operation = "operation" in header  # Get the Operations requested
            file_name = "file_name" in header  # Get the file name

            # First Operations : GET FILES
            if operation == Operation.GET_FILES.value:
                metadata = self.get_files()  # Get all the files from the current directory
                self.send_header(client, operation, "", 0)

            elif operation == Operation.DOWNLOAD.value:
                size = os.path.getsize(file_name)
                
            elif operation == Operation.UPLOAD.value:
                size = 'null'

