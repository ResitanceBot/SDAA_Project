import socket

UDP_PORT = 1234
UDP_IP_SENDER = ''

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP_SENDER, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024)
    print("Received message:")
    print(data.decode('utf-8'))
    print("From address:", addr)