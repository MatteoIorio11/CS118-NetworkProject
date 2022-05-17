import hashlib
import socket as sk
import time
import json
import base64
import os
from ClientServerUDP.Client.HeaderBuilder import HeaderBuilder
from ClientServerUDP.Client.Operation import Operation
import math


class Client:
    server_address = ''
    port = 0
    def __init__(self):
        self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
    
    def set_server_adress(self, server_address, port):
        #storing the IP and Port of the server
        self.server_address = server_address
        self.port = port
        
    def get_files_on_server(self):
        header = HeaderBuilder.build_header(Operation.GET_FILES.value, True, hash(''), "", 0, "".encode())    #create header for getting files
        self.send(header)
        data = self.sock.recv(4096)
        data_json = json.loads(data.decode())
        if not data_json['status'] :    #if something whent wrong
            raise Exception(base64.b64decode(data_json['metadata']))
        files = base64.b64decode(data_json['metadata'])    #decode files name
        return files.decode()
        
    def get_menu(self):
        header = HeaderBuilder.build_header(Operation.OPEN_CONNECTION.value, True, hash(''), "", 0, "".encode())    #create header for getting the menu
        self.send(header)
        data = self.sock.recv(4096)
        data_json = json.loads(data.decode())
        if not data_json['status'] :    #if something whent wrong
            raise Exception(base64.b64decode(data_json['metadata']))
        menu = base64.b64decode(data_json['metadata'])    #decode menu
        return menu.decode()
    
    def download_file(self, file_name):
        while True:
            header = HeaderBuilder.build_header(Operation.DOWNLOAD.value, True, hash(''), file_name, 0, "".encode())    #create header for downloading a file
            self.send(header)
            ack = self.sock.recv(4096)    #waiting for an ack from the server
            ack_json = json.loads(ack.decode())
            if not ack_json['status'] or ack_json['operation'] != Operation.ACK.value:
                raise Exception(base64.b64decode(ack_json['metadata']).decode())
            #now the server is ready to send packets and the client to receive them
            tot_packs = int(base64.b64decode(ack_json['metadata']).decode())   #tot packs that i should receive
            buffer_size = 12_000
            cont_packs = 0
            md5_hash = hashlib.md5()
            with open(file_name,'wb') as f:
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
            #not all packs have been arrived
                
    
    def upload(self, file):
        while True:
            if file in os.listdir(os.getcwd()):
                buffer_size = 8192
                tot_packs = math.ceil(os.path.getsize(os.path.join(os.getcwd(), file))/buffer_size)
                upload_request = HeaderBuilder.build_header(Operation.UPLOAD.value, True, hash(''), file, 0, str(tot_packs).encode())    #creating header for uploading file
                self.send(upload_request)
                ack = self.sock.recv(4096)    #waiting for an ack from the server
                ack_json = json.loads(ack.decode())
                if not ack_json['status'] or ack_json['operation'] != Operation.ACK.value:
                    raise Exception(base64.b64decode(ack_json['metadata']))
                #now the client is ready to send packets and the server to receive them
                cont_packs = 0
                print('\n\r Sending the file %s to the destination' % str(file))
                with open(os.path.join(os.getcwd(), file), 'rb') as handle:
                    byte = handle.read(buffer_size)   #Read buffer_size bytes from the file
                    cont_packs += 1
                    while byte:
                        header = HeaderBuilder.build_header(Operation.UPLOAD.value, True, hash(''), file, buffer_size, byte)  # Send the read bytes to the Client
                        self.send(header)
                        percent = int(cont_packs*100/tot_packs)
                        cont_packs += 1
                        print("{:03d}".format(percent), "%", end='\r')
                        time.sleep(0.001)
                        byte = handle.read(buffer_size)   #Read buffer_size bytes from the file
                header = HeaderBuilder.build_header( Operation.END_FILE.value, True, hash(''),
                                                     "", 0, "".encode())  #Telling to the server that the file is complete
                self.send(header)
            else:
                print("The input file does not exit!")
            final_ack = self.sock.recv(4096)    #waiting for an ack from the server
            final_ack_json = json.loads(final_ack.decode())
            if not final_ack_json['status']:
                print("\nSomething went wrong during the upload trying again...\n")
            else:
                print("\nFile correctly uploaded!\n")
                break

    def send(self, message):
        self.sock.sendto(message.encode(), (self.server_address, self.port))
        time.sleep(0.001)

    def close_connection(self):
        self.sock.close()


def main():
    client = Client()
    try:
        client.set_server_adress('localhost', 20000)
        menu = client.get_menu()
        while True:
            print(menu)
            operation = int(input("Select an operation among the ones above: "))
            if operation == 1:
                print(client.get_files_on_server())
            elif operation == 2:
                file = input("Write the name of the file that you want to download ")
                client.download_file(file)
            elif operation == 3:
                file = input("Write the name of the file that you want to upload on the server ")
                client.upload(file)
            elif operation == 4:
                client.close_connection()
                break
            else:
                print("Wrong number")
        
        time.sleep(1)
    except Exception as info:
        print(info)
    finally:
        client.close_connection()


if __name__ == "__main__":
    main()
