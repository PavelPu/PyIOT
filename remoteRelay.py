import socket

class RemoteRelay:
    def getAll (self):
        #self.sock.sendto(bytes("!GetIP\r","ascii"), (self.UDP_IP, self.UDP_PORT))
        self.sock.sendto(bytes("!GetAll\r", "ascii"), (self.UDP_IP, self.UDP_PORT))
        #try:
        data, server = self.sock.recvfrom(1024)
        print(data)
        #except:
        #    print("bad")


    def __init__(self):
        self.UDP_IP = "192.168.8.100"
        self.UDP_LIP = "192.168.8.103"
        self.UDP_PORT = 7777
        self.sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        self.sock.settimeout(1)
        self.sock.bind((self.UDP_LIP, self.UDP_PORT))

def main():

    MESSAGE_GET = "!GetAll"
    remRelay = RemoteRelay()
    #remRelay.sock = socket.socket(socket.AF_INET, # Internet
    #                 socket.SOCK_DGRAM) # UDP
    #remRelay.sock.settimeout(1)
    #remRelay.sock.bind((remRelay.UDP_LIP, remRelay.UDP_PORT))
    #remRelay.sock.sendto(bytes(MESSAGE_GET,"ascii"), ("192.168.8.100", 7777))
    remRelay.getAll()
if __name__=="__main__":
    main()