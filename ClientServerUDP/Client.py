import socket as sk
import time

class Client:
    def __init__(self):
        self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
    
    def send(self, message, server_address, port):
        # inviate il messaggio
        print ('sending "%s"' % message)
        time.sleep(2) #attende 2 secondi prima di inviare la richiesta
        sent = sock.sendto(message.encode(), (server_address, port))
        
        # Ricevete la risposta dal server
        print('waiting to receive from')
        data, server = sock.recvfrom(4096)
        return data.decode('utf8')



client = Client()

message = 'Questo è il corso di ?'

try:

    # inviate il messaggio
    data = client.send(message, 'localhost', 20000)
    #print(server)
    time.sleep(2)
    print ('received message "%s"' % data)
except Exception as info:
    print(info)
finally:
    print ('closing socket')
    sock.close()
