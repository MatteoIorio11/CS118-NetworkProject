import socket as sk
import time
import json
import base64
import os
from ClientServerUDP.HeaderBuilder import HeaderBuilder
from ClientServerUDP.Operation import Operation


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
        data = self.sock.recv()
        data_json = json.loads(data.decode())
        if not data_json['status'] :
            raise Exception(base64.b64decode(data_json['metadata']))
        files = base64.b64decode(data_json['metadata'])
        
        return files
        
    def download_file(self, file_name):
        header = HeaderBuilder.build_header(Operation.DOWNLOAD.value, True, file_name, 0, "".encode())
        self.send(header)
        buffer_size = 12_000
        with open(file_name,'wb') as f:
            while True:
                data = self.sock.recv(buffer_size)
                data_json = json.loads(data.decode())
                if not data_json['status']:
                    raise Exception(base64.b64decode(data_json['metadata']))
                if data_json['operation'] == Operation.END_FILE.value:
                    break
                file = base64.b64decode(data_json['metadata'])
                f.write(file)
    
    def upload(self, file):
        buffer_size = 8192
        if file in os.listdir(os.getcwd()):
            print('\n\r Sending the file %s to the destination', str(file))
            with open(os.path.join(os.getcwd(), file), 'rb') as handle:
                byte = handle.read(buffer_size)   # Read a buffer size
                while byte:
                    header = HeaderBuilder.build_header(Operation.UPLOAD.value, True, file, buffer_size, byte)  # Send the read bytes to the Client
                    self.send(header)
                    time.sleep(0.01)
                    byte = handle.read(buffer_size)   # Read a buffer size
            header = HeaderBuilder.build_header( Operation.END_FILE.value, True,
                                                 "", 0, "".encode())  # Send the bytes read to the Client
            self.send(header)
        else:
            header = HeaderBuilder.build_header(Operation.ERROR.value, False,
                                                "", 0, "The input file does not exist in the directory".encode())
            self.send(header)

    def send(self, message):
        print ('sending "%s"' % message)
        self.sock.sendto(message.encode(), (self.server_address, self.port))
        time.sleep(0.01)

    def close_connection(self):
        self.sock.close()


def main():
    client = Client()

    try:

        client.set_server_adress('localhost', 20000)
        client.upload("test.pdf")
        time.sleep(1)
    except Exception as info:
        print(info)
    finally:
        print ('closing socket')
        client.close_connection()


if __name__ == "__main__":
    main()