import socket

UDP_RECEIVER_IP = '192.168.100.34' 
UDP_PORT = 1234
UDP_PAYLOAD = 'CODE'

def yes_or_no(question):
    reply = str(input(question)).lower().strip()
    if reply[0] == 'y':
        return 0
    elif reply[0] == 'n':
        return 1
    else:
        return yes_or_no("Please Enter (y/n) ")
		
while True:
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(bytes(UDP_PAYLOAD, "utf-8"), (UDP_RECEIVER_IP, UDP_PORT))    
		sock.close()
		print("UDP target IP:", UDP_RECEIVER_IP)
		print("UDP target port:", UDP_PORT)
		print("message:", UDP_PAYLOAD)
		if(yes_or_no('Send again (y/n): ')):
			break
	except:
		pass

