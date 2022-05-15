from Operation import Operation
import socket as sk
import time
import json
import os
import yaml
import base64


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
    port = 0                              # The port where the Server is listening
    address = ''                          # The address of the Server
    buffer_size = 0                       # How much is big the buffer for reading files
    time_to_sleep = 0                     # How much time the Server has to sleep before to send another package
    socket = 0                            # Server's socket
    path = os.path.join(os.getcwd(), 'Server') #
    error_flag = 0                        # Flag used in order to notify the client of an internal error

    # Define the constructor of the Server
    def __init__(self):
        file = os.path.join(self.path,'config.yaml')  # path of the configuration file
        with open(file, 'r') as file:
            dictionary = yaml.load(file, Loader=yaml.FullLoader)
        self.address = str(dictionary['address'])
        self.port = dictionary['port']
        self.buffer_size = dictionary['buffer_size']
        self.time_to_sleep = dictionary['time_to_sleep']
        self.path = os.path.join(self.path, dictionary['path'])
        self.socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

    # Argument : self
    # This method set the server address -> set the IP and the PORT and then the creation of the Server's socket
    def start_server(self):
        server_address = (self.address, self.port)
        print('\n\r starting up the server on ip : %s  and port : %s' % server_address)
        self.socket.bind(server_address)
        self.launch_server()  # Launch the Server's main application

    # Argument : self
    # Return : All the files in the current directory
    # This method get all the files in the current directory of the server
    def get_files(self):
        print('\n\r Received command : "list files" ')
        list_directories = os.listdir(self.path)
        metadata = ''.join([(str(directory)+"\n") for directory in list_directories])
        print('\n\r Sending all the files in the Directory...')
        self.error_flag = 0  # No errors, the flag is false
        return metadata

    # Argument : file
    # Argument : client
    # This method read multiple chunks of the selected file, after every chunk
    # the Server send It to the Client. The chunk size is 8192 bytes
    def download(self, file, client):
        if file in os.listdir(self.path):
            print('\n\r Sending the file %s to the destination', str(file))
            with open(os.path.join(self.path, file), 'rb') as handle:
                byte = handle.read(self.buffer_size)   # Read a buffer size
                while byte:
                    self.build_header(client, Operation.SENDING_FILE.value, file, self.buffer_size, byte)  # Send the read bytes to the Client
                    time.sleep(self.time_to_sleep)
                    byte = handle.read(self.buffer_size)   # Read a buffer size
            self.build_header(client, Operation.END_FILE.value, "", 0, "".encode())  # Send the bytes read to the Client
            self.error_flag = 0  # No errors the file is in the current directory of the Server
        else:
            self.error_flag = 1  # The selected file does not exist in the current directory of the Server
            self.build_header(client, Operation.ERROR.value, "", 0, "The input file does not exist in the directory".encode())

    # Argument : self
    # Argument : file
    # Argument : metadata_files
    # Return
    # This method write the metadata in input inside the new file named : file.
    def upload(self, file, metadata_files, client):
        if file in os.listdir(self.path):
            self.error_flag = 1
            self.build_header(client, Operation.ERROR.value, "", 0, "The input file does not exist in the directory")
        else:
            self.error_flag = 0

    # Argument : self
    # Argument : destination
    # Argument : data
    # This method send a UDP package
    def send_package(self, destination, data):
        self.socket.sendto(data.encode(), destination)
        time.sleep(self.time_to_sleep)

    # Argument : self
    # Argument : destination    < The Client >
    # Argument : operation      < Which Operations is sent (see Operation.py) >
    # Argument : file:name      < What is the name of the requested\sent file >
    # Argument : Size           < The size of the file_name >
    # This method create the header file and then the Server send it to the client
    def build_header(self, destination, operation, file_name, size, metadata):
        header = {"operation": operation,"file_name": file_name,"status": False if self.error_flag == 1 else True,"size": size,"metadata": base64.b64encode(metadata).decode('ascii')}
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
            operation = header['operation']# Get the Operations requested
            file_name = header['file_name']  # Get the file name
            #print(header)
            # First Operations : GET FILES
            if operation == Operation.GET_FILES.value:
                metadata = self.get_files()
                self.build_header(client, operation, "", metadata.__len__(), metadata.encode())

            elif operation == Operation.DOWNLOAD.value:
                self.download(file_name,client)
                
            elif operation == Operation.UPLOAD.value:
                size = 'null'

