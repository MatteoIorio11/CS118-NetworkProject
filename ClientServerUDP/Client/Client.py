import hashlib
import time
import json
import base64
import os
import math
import socket as sk
from HeaderFactory import HeaderFactory
from Operation import Operation
from Utils import Util


class Client:
    server_address = ''
    port = 0
    path = os.path.join(os.getcwd(), 'Client')
    timeout = 0

    def __init__(self):
        file = os.path.join(self.path, 'config.json')  # path of the configuration file
        with open(file, 'r') as file:
            dictionary = json.load(file)
        self.buffer_size = dictionary['buffer_size']
        self.time_to_sleep = dictionary['time_to_sleep']
        self.path = os.path.join(self.path, dictionary['path'])
        self.timeout = dictionary['timeout']
        self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

    def set_server_adress(self, server_address, port):
        # storing the IP and Port of the server
        self.server_address = server_address
        self.port = port
        
    def get_files_on_server(self):
        header = HeaderFactory.build_operation_header_wchecksum(Operation.GET_FILES.value,
                                                    Util.get_hash_with_metadata('ACK'.encode()),
                                                    "ACK".encode())    # create header for getting files
        self.send(header)
        try :
            self.sock.settimeout(self.timeout)
            data = self.sock.recv(4096)
            data_json = json.loads(data.decode())
            res = Util.get_hash_with_metadata(base64.b64decode(data_json['metadata']))
            if not data_json['status'] or res != data_json['checksum']:    # if something whent wrong
                print('Error ', base64.b64decode(data_json['metadata']))
                return
            files = base64.b64decode(data_json['metadata'])    # decode files name
            self.sock.settimeout(None)
            return files.decode()
        except sk.timeout as e:
            self.sock.settimeout(None)
            print(" ---- SOCKET TIMEOUT ----")
            return "Error in the operation, please try again."
        
    def get_menu(self):
        header = HeaderFactory.build_operation_header_wchecksum(Operation.OPEN_CONNECTION.value,
                                                      Util.get_hash_with_metadata('ACK'.encode()),
                                                      "ACK".encode())    # create header for getting the menu
        self.send(header)
        try:
            self.sock.settimeout(self.timeout)
            data = self.sock.recv(4096)
            data_json = json.loads(data.decode())
            if not data_json['status'] or \
                    Util.get_hash_with_metadata(base64.b64decode(data_json['metadata'])) != data_json['checksum']:
                # if something whent wrong
                print('Error ', base64.b64decode(data_json['metadata']))
                return
            menu = base64.b64decode(data_json['metadata'])    # decode menu
            self.sock.settimeout(None)
            return menu.decode()
        except sk.timeout as e:
            self.sock.settimeout(None)
            print(" ---- SOCKET TIMEOUT ----- ")
            print("The Client can't get the Menu. Maybe the Server is OFFLINE.")

    def download_file(self, file_name):
        try:
            tries = 1
            self.sock.settimeout(self.timeout)
            while True:
                error = False
                header = HeaderFactory.build_operation_header_wfile(Operation.DOWNLOAD.value, file_name,
                                                                    Util.get_hash_with_metadata('ACK'.encode()), "ACK".encode())
                self.send(header)
                ack = self.sock.recv(4096)    # waiting for an ack from the server
                ack_json = json.loads(ack.decode())
                if not ack_json['status'] or ack_json['operation'] != Operation.ACK.value:
                    print('Error ', base64.b64decode(ack_json['metadata']).decode())
                    return
                # now the server is ready to send packets and the client to receive them
                tot_packs = int(base64.b64decode(ack_json['metadata']).decode())   # tot packs that i should receive
                buffer_size = 12_000
                cont_packs = 0
                md5_hash = hashlib.md5()
                with open(os.path.join(self.path, file_name),'wb') as f:
                    while True:
                        data = self.sock.recv(buffer_size)
                        data_json = json.loads(data.decode())
                        Util.update_md5(md5_hash, base64.b64decode(data_json['metadata']))
                        calculate_hash = Util.get_digest(md5_hash)
                        checksum = str(data_json['checksum'])
                        if not data_json['status']:
                            print('Error ',base64.b64decode(data_json['metadata']))
                            return
                        elif calculate_hash != checksum:
                            print("Something went wrong during the download trying again")
                            error = True
                            ack = HeaderFactory.build_error_header(Util.get_hash_with_metadata(
                                                                   "Not all packages have been arrived".encode()),
                                                                   "Not all packages have been arrived".encode())
                            self.send(ack)
                            time.sleep(0.5)
                            break
                        if data_json['operation'] == Operation.END_FILE.value:
                            break
                        else:
                            cont_packs += 1
                        percent = int(cont_packs*100/tot_packs)    # calculating percentage of downloaded packet
                        print("{:02d}".format(percent), "%", end='\r')    # printing percentage
                        file = base64.b64decode(data_json['metadata'])
                        f.write(file)    # write the read bytes

                if tot_packs == cont_packs and error == False:    # all packs have been arrived
                    print("\nThe file has been downloaded correctly\n")
                    self.sock.settimeout(None)
                    break
                print("\nNot all packets have been arrived downloading again...\n")
                tries = tries + 1
                if tries > 5:
                    print("Tried five times. EXIT THE OPERATION...")
                    self.sock.settimeout(None)
                    break
                # not all packs have been arrived
        except sk.timeout as e:
            self.sock.settimeout(None)
            print(" ---- SOCKET TIMEOUT ----- ")
            print("Socket timeout. EXIT THE OPERATION...")

    def upload(self, file):
        tries = 1 # How much time the Client has tried to send the package to the Server.
        try:
            self.sock.settimeout(self.timeout)
            while True:
                if file in os.listdir(self.path):
                    buffer_size = self.buffer_size
                    tot_packs = math.ceil(os.path.getsize(os.path.join(self.path, file))/buffer_size)
                    upload_request = HeaderFactory.build_operation_header_wfile(Operation.UPLOAD.value, file,
                                                                Util.get_hash_with_metadata(str(tot_packs).encode()),
                                                                str(tot_packs).encode())    # creating header for uploading file
                    self.send(upload_request)
                    ack = self.sock.recv(4096)    # waiting for an ack from the server
                    ack_json = json.loads(ack.decode())
                    checksum = ack_json['checksum']
                    if not ack_json['status'] or ack_json['operation'] != Operation.ACK.value\
                            or checksum != Util.get_hash_with_metadata('ACK'.encode()):
                                print('Error in the Upload. Something went wrong please try again...')
                                return
                    # now the client is ready to send packets and the server to receive them
                    cont_packs = 0
                    print('\n\r Sending the file %s to the destination' % str(file))
                    md5 = hashlib.md5()
                    with open(os.path.join(self.path, file), 'rb') as handle:
                        byte = handle.read(buffer_size)   #Read buffer_size bytes from the file
                        cont_packs += 1
                        md5 = Util.update_md5(md5, byte)
                        while byte:
                            header = HeaderFactory.build_operation_header_wchecksum(Operation.UPLOAD.value,
                                                                Util.get_digest(md5),
                                                                byte)  # Send the read bytes to the Client
                            self.send(header)
                            percent = Util.get_percentage(cont_packs, tot_packs)
                            cont_packs += 1
                            print("{:03d}".format(percent), "%", end='\r')
                            byte = handle.read(buffer_size)   # Read buffer_size bytes from the file
                            md5 = Util.update_md5(md5, byte)
                    md5 = Util.update_md5(md5, 'ACK'.encode())
                    header = HeaderFactory.build_operation_header_wchecksum(Operation.END_FILE.value,
                                                        Util.get_digest(md5),
                                                         "ACK".encode())  # Telling the server that the file is complete
                    self.send(header)
                else:
                    self.sock.settimeout(None)
                    print("\nThe input file does not exit!\n")
                    break
                final_ack = self.sock.recv(4096)    # waiting for an ack from the server
                final_ack_json = json.loads(final_ack.decode())
                if not final_ack_json['status']:
                    print("\nSomething went wrong during the upload trying again...\n")
                    tries = tries + 1
                    if tries > 5:
                        self.sock.settimeout(None)
                        print("Tried five times. EXIT THE OPERATION...\n")
                        break
                    time.sleep(0.5)
                else:
                    self.sock.settimeout(None)
                    print("\nFile correctly uploaded!\n")
                    break
        except sk.timeout as e:
            self.sock.settimeout(None)
            print(" ---- SOCKET TIMEOUT ----- ")
            print("The timeout is over, exit the operation...")

    def send(self, message):
        self.sock.sendto(message.encode(), (self.server_address, self.port))
        time.sleep(self.time_to_sleep)

    def close_connection(self):
        self.sock.close()
