import socket as sk
import time
import json
from ClientServerUDP.Operation import Operation

class Client:
    def __init__(self):
        self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
    
    def set_server_adress(self, server_address, port):
        self.server_address = server_address
        self.port = port
    
    def create_header(self, operation, file_name, status):
        header = {"operation": operation,"file_name": file_name, "status": status}
        return json.dumps(header)
        
    def get_files_on_server(self):
        files = self.send(self.create_header(Operation.GET_FILES.value, "", True))
        
        return json.loads(files.decode())['metadata']
        
    def download_file(self, file_name):
        response = self.send()
    
    def send(self, message):
        print ('sending "%s"' % message)
        self.sock.sendto(message.encode(), (self.server_address, self.port))
        
        print('waiting to receive from')
        data, server = self.sock.recvfrom(4096)
        data = json.loads(data.decode('utf8'))
        if(data['status'] == True):
            self.sock.sendto(self.create_header(Operation.ACK.value, "", True).encode(), (self.server_address, self.port))
            response, server = self.sock.recvfrom(4096)
        else:
            raise Exception("Failed")
        return response

    def close_connection(self):
        self.sock.close()


def main():
    client = Client()

    message = 'Questo è il corso di ?'

    try:

        client.set_server_adress('localhost', 20000)
        data = client.get_files_on_server()
        time.sleep(1)
        print (data)
    except Exception as info:
        print(info)
    finally:
        print ('closing socket')
        client.close_connection()


if __name__ == "__main__":
    main()