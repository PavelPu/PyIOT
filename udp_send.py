
import socket

UDP_IP = "192.168.8.100"
UDP_LIP = "192.168.8.103"
UDP_PORT = 7777
MESSAGE_GET = "!GetAll" + "\r"
MESSAGE2 = "!SetR1_2" + "\r"
MESSAGE = "!SetR1_1" + "\r"

print ("UDP target IP:", UDP_IP)
print ("UDP target port:", UDP_PORT)
print ("message:", MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.settimeout(1)
sock.bind((UDP_LIP, UDP_PORT))

sock.sendto(bytes(MESSAGE,"ascii"), (UDP_IP, UDP_PORT))
data, server = sock.recvfrom(1024)
print(data)
sock.sendto(bytes(MESSAGE2,"ascii"), (UDP_IP, UDP_PORT))
data, server = sock.recvfrom(1024)
print(data)
sock.sendto(bytes(MESSAGE_GET,"ascii"), (UDP_IP, UDP_PORT))
#sock.sendto(bytes("!GetIP\r","ascii"), (UDP_IP, UDP_PORT))

data, server = sock.recvfrom(1024)
print(data)

