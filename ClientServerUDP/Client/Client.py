import hashlib
import time
import json
import base64
import os
import math
import socket as sk
from HeaderFactory import HeaderFactory
from Operation import Operation


class Client:
    server_address = ''
    port = 0
    path = os.path.join(os.getcwd(), 'Client')

    def __init__(self):
        file = os.path.join(self.path, 'config.json')  # path of the configuration file
        with open(file, 'r') as file:
            dictionary = json.load(file)
        self.buffer_size = dictionary['buffer_size']
        self.time_to_sleep = dictionary['time_to_sleep']
        self.path = os.path.join(self.path, dictionary['path'])
        self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

    def set_server_adress(self, server_address, port):
        # storing the IP and Port of the server
        self.server_address = server_address
        self.port = port
        
    def get_files_on_server(self):
        md5_hash = hashlib.md5()
        md5_hash.update('ACK'.encode())
        header = HeaderFactory.build_operation_header_wchecksum(Operation.GET_FILES.value, md5_hash.hexdigest(),
                                                      "ACK".encode())    # create header for getting files
        self.send(header)
        data = self.sock.recv(4096)
        data_json = json.loads(data.decode())
        md5_hash = hashlib.md5()
        md5_hash.update(base64.b64decode(data_json['metadata']))
        res = md5_hash.hexdigest()
        if not data_json['status'] or res != data_json['checksum']:    # if something whent wrong
            raise Exception(base64.b64decode(data_json['metadata']))
        files = base64.b64decode(data_json['metadata'])    # decode files name
        return files.decode()
        
    def get_menu(self):
        md5_hash = hashlib.md5()
        md5_hash.update('ACK'.encode())
        header = HeaderFactory.build_operation_header_wchecksum(Operation.OPEN_CONNECTION.value, md5_hash.hexdigest(),
                                                      "ACK".encode())    # create header for getting the menu
        self.send(header)
        data = self.sock.recv(4096)
        data_json = json.loads(data.decode())
        md5_hash = hashlib.md5()
        md5_hash.update(base64.b64decode(data_json['metadata']))
        if not data_json['status'] or md5_hash.hexdigest() != data_json['checksum']:    # if something whent wrong
            raise Exception(base64.b64decode(data_json['metadata']))
        menu = base64.b64decode(data_json['metadata'])    #decode menu
        return menu.decode()
    
    def download_file(self, file_name):
        while True:
            md5 = hashlib.md5()
            md5.update("ACK".encode())
            header = HeaderFactory.build_operation_header_wfile(Operation.DOWNLOAD.value, file_name,md5.hexdigest(), "ACK".encode())
            self.send(header)
            ack = self.sock.recv(4096)    # waiting for an ack from the server
            ack_json = json.loads(ack.decode())
            if not ack_json['status'] or ack_json['operation'] != Operation.ACK.value:
                raise Exception(base64.b64decode(ack_json['metadata']).decode())
            # now the server is ready to send packets and the client to receive them
            tot_packs = int(base64.b64decode(ack_json['metadata']).decode())   # tot packs that i should receive
            buffer_size = 12_000
            cont_packs = 0
            md5_hash = hashlib.md5()
            with open(os.path.join(self.path, file_name),'wb') as f:
                while True:
                    data = self.sock.recv(buffer_size)
                    data_json = json.loads(data.decode())
                    md5_hash.update(base64.b64decode(data_json['metadata']))
                    calculate_hash = md5_hash.hexdigest()
                    checksum = str(data_json['checksum'])
                    print(calculate_hash + " " + checksum)
                    if not data_json['status'] or calculate_hash != checksum:
                        raise Exception(base64.b64decode(data_json['metadata']))
                    if data_json['operation'] == Operation.END_FILE.value:
                        break
                    else:
                        cont_packs += 1
                    percent = int(cont_packs*100/tot_packs)    # calculating percentage of downloaded packet
                    print("{:02d}".format(percent), "%", end='\r')    # printing percentage
                    file = base64.b64decode(data_json['metadata'])
                    f.write(file)    # write the read bytes
            print("tot: ", tot_packs, "cont: ", cont_packs)
            if tot_packs == cont_packs:    # all packs have been arrived
                print("\nThe file has been downloaded correctly\n")
                break
            print("\nNot all packets have been arrived downloading again...\n")
            # not all packs have been arrived

    def upload(self, file):
        while True:
            if file in os.listdir(self.path):
                buffer_size = self.buffer_size
                tot_packs = math.ceil(os.path.getsize(os.path.join(self.path, file))/buffer_size)
                md5 = hashlib.md5()
                md5.update(str(tot_packs).encode())
                upload_request = HeaderFactory.build_operation_header_wfile(Operation.UPLOAD.value, file, md5.hexdigest(),
                                                            str(tot_packs).encode())    # creating header for uploading file
                self.send(upload_request)
                ack = self.sock.recv(4096)    # waiting for an ack from the server
                ack_json = json.loads(ack.decode())
                md5 = hashlib.md5()
                md5.update(base64.b64decode(ack_json['metadata']))
                checksum = ack_json['checksum']
                if not ack_json['status'] or ack_json['operation'] != Operation.ACK.value or checksum != md5.hexdigest():
                    raise Exception(base64.b64decode(ack_json['metadata']))
                # now the client is ready to send packets and the server to receive them
                cont_packs = 0
                print('\n\r Sending the file %s to the destination' % str(file))
                md5 = hashlib.md5()
                with open(os.path.join(self.path, file), 'rb') as handle:
                    byte = handle.read(buffer_size)   #Read buffer_size bytes from the file
                    cont_packs += 1
                    md5.update(byte)
                    while byte:
                        header = HeaderFactory.build_operation_header(Operation.UPLOAD.value, md5.hexdigest(),
                                                            byte)  # Send the read bytes to the Client
                        self.send(header)
                        percent = int(cont_packs*100/tot_packs)
                        cont_packs += 1
                        print("{:03d}".format(percent), "%", end='\r')
                        byte = handle.read(buffer_size)   # Read buffer_size bytes from the file
                        md5.update(byte)
                md5.update('ACK'.encode())
                header = HeaderFactory.build_operation_header(Operation.END_FILE.value, md5.hexdigest(),
                                                     "ACK".encode())  # Telling to the server that the file is complete
                self.send(header)
            else:
                print("\nThe input file does not exit!\n")
                break
            final_ack = self.sock.recv(4096)    # waiting for an ack from the server
            final_ack_json = json.loads(final_ack.decode())
            if not final_ack_json['status']:
                print("\nSomething went wrong during the upload trying again...\n")
            else:
                print("\nFile correctly uploaded!\n")
                break

    def send(self, message):
        self.sock.sendto(message.encode(), (self.server_address, self.port))
        time.sleep(self.time_to_sleep)

    def close_connection(self):
        self.sock.close()
