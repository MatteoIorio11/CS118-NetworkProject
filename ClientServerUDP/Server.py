import socket as sk
import time

# Creiamo il socket
sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

# associamo il socket alla porta
server_address = ('localhost', 10000)
print('\n\r starting up on %s port %s' % server_address)
sock.bind(server_address)

while True:
    print('\n\r waiting to receive message...')
    data, address = sock.recvfrom(4096)

    print('received %s bytes from %s' % (len(data), address))
    print(data.decode('utf8'))

    if data:
        data1 = 'Programmazione di Reti'
        time.sleep(2)
        sent = sock.sendto(data1.encode(), address)
        print('sent %s bytes back to %s' % (sent, address))

