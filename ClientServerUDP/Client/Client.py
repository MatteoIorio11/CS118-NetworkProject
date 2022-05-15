import socket as sk
import time
import json
from Operation import Operation
import base64

class Client:
    def __init__(self):
        self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
    
    def set_server_adress(self, server_address, port):
        self.server_address = server_address
        self.port = port
    
    def create_header(self, operation, file_name, status, size, metadata):
        header = {"operation": operation,"file_name": file_name, "status": status, "size": size, "metadata": metadata}
        return json.dumps(header)
        
    def get_files_on_server(self):
        files = self.send(self.create_header(Operation.GET_FILES.value, "", True, 0, ""))
        
        return json.loads(files.decode())['metadata']
        
    def download_file(self, file_name):
        header = self.create_header(Operation.DOWNLOAD.value, file_name, True, 0, "")
        self.send(header)
        buffersize = 12000         
        with open(file_name,'wb') as f:
           while True:
                data = self.sock.recv(buffersize)
                data_json = json.loads(data.decode())
                if(data_json['status'] == False):
                    raise Exception(base64.b64decode(data_json['metadata']))
                if data_json['operation'] == Operation.END_FILE.value:
                    break
                file = base64.b64decode(data_json['metadata'])
                f.write(file)
    
    
    
    def send(self, message):
        print ('sending "%s"' % message)
        self.sock.sendto(message.encode(), (self.server_address, self.port))

    def close_connection(self):
        self.sock.close()


def main():
    client = Client()

    message = 'Questo è il corso di ?'

    try:

        client.set_server_adress('localhost', 20000)
        client.download_file("test.txt")
        time.sleep(1)
    except Exception as info:
        print(info)
    finally:
        print ('closing socket')
        client.close_connection()


if __name__ == "__main__":
    main()