import socket as sk
import time
import json
import base64
import os
from HeaderBuilder import HeaderBuilder
from Operation import Operation


class Client:
    server_address = ''
    port = 0
    def __init__(self):
        self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
    
    def set_server_adress(self, server_address, port):
        self.server_address = server_address
        self.port = port
        
    def get_files_on_server(self):
        header = HeaderBuilder.build_header(Operation.GET_FILES.value, True, "", 0, "".encode())
        self.send(header)
        data = self.sock.recv(4096)
        data_json = json.loads(data.decode())
        if not data_json['status'] :
            raise Exception(base64.b64decode(data_json['metadata']))
        files = base64.b64decode(data_json['metadata'])
        return files.decode()
        
    def get_menu(self):
        header = HeaderBuilder.build_header(Operation.OPEN_CONNECTION.value, True, "", 0, "".encode())
        self.send(header)
        data = self.sock.recv(4096)
        data_json = json.loads(data.decode())
        if not data_json['status'] :
            raise Exception(base64.b64decode(data_json['metadata']))
        menu = base64.b64decode(data_json['metadata'])
        return menu.decode()
    
    def download_file(self, file_name):
        header = HeaderBuilder.build_header(Operation.DOWNLOAD.value, True, file_name, 0, "".encode())
        self.send(header)
        ack = self.sock.recv(4096)
        ack_json = json.loads(ack.decode())
        if not ack_json['status'] or ack_json['operation'] != Operation.ACK.value:
            raise Exception(base64.b64decode(ack_json['metadata']).decode())
        tot_packs = float(base64.b64decode(ack_json['metadata']).decode())
        buffer_size = 12_000
        cont_packs = 0
        with open(file_name,'wb') as f:
            while True:
                data = self.sock.recv(buffer_size)
                data_json = json.loads(data.decode())
                cont_packs += 1
                percent = int(cont_packs*100/tot_packs)
                print("{:02d}".format(percent), "%", end='\r')       
                if not data_json['status']:
                    raise Exception(base64.b64decode(data_json['metadata']))
                if data_json['operation'] == Operation.END_FILE.value:
                    break
                file = base64.b64decode(data_json['metadata'])
                f.write(file)
    
    def upload(self, file):
        upload_request = HeaderBuilder.build_header(Operation.UPLOAD.value, True, file, 0, "".encode())
        self.send(upload_request)
        ack = self.sock.recv(4096)
        ack_json = json.loads(ack.decode())
        if not ack_json['status'] or ack_json['operation'] != Operation.ACK.value:
            raise Exception(base64.b64decode(ack_json['metadata']))
        buffer_size = 8192
        cont_packs = 0
        if file in os.listdir(os.getcwd()):
            tot_packs = os.path.getsize(os.path.join(os.getcwd(), file))/buffer_size
            print('\n\r Sending the file %s to the destination', str(file))
            with open(os.path.join(os.getcwd(), file), 'rb') as handle:
                byte = handle.read(buffer_size)   # Read a buffer size
                cont_packs += 1
                while byte:
                    header = HeaderBuilder.build_header(Operation.UPLOAD.value, True, file, buffer_size, byte)  # Send the read bytes to the Client
                    self.send(header)
                    cont_packs += 1
                    percent = int(cont_packs*100/tot_packs)
                    print("{:03d}".format(percent), "%", end='\r')
                    time.sleep(0.001)
                    byte = handle.read(buffer_size)   # Read a buffer size
            header = HeaderBuilder.build_header( Operation.END_FILE.value, True,
                                                 "", 0, "".encode())  # Send the bytes read to the Client
            self.send(header)
        else:
            print("The input file does not exit!")

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
