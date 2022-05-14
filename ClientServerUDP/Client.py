import socket as sk
import time
import json

class Client:
    def __init__(self):
        self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
    
    def set_server_adress(self, server_address, port):
        self.server_address = server_address
        self.port = port
        
    def get_files_on_server(self):
        header = {"operation": 1, "status": True}
        data = json.dumps(header)
        self.send(data)
        
    
    def send(self, message):
        print ('sending "%s"' % message)
        sent = sock.sendto(message.encode(), (self.server_address, self.port))
        
        print('waiting to receive from')
        data, server = sock.recvfrom(4096)
        return data



client = Client()

message = 'Questo è il corso di ?'

try:

    client.open_connection('localhost', 20000)
    # inviate il messaggio
    data = client.send(message)
    #print(server)
    time.sleep(2)
    print ('received message "%s"' % data)
except Exception as info:
    print(info)
finally:
    print ('closing socket')
    sock.close()
