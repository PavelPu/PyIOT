import socket

class RemoteRelay:
    def getAll (self):
        self.sock.sendto(bytes("!GetAll\n", "ascii"), (self.UDP_IP, self.UDP_PORT))
        try:
            data, server = self.sock.recvfrom(1024)
            print(data)
        except:
            print("bad")


    def __init__(self):
        self.UDP_IP = "192.168.8.100"
        self.UDP_LIP = "127.0.0.1"
        self.UDP_PORT = 7777
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.sock.settimeout(1)
        self.sock.bind((self.UDP_LIP, self.UDP_PORT))

def main():


    remRelay = RemoteRelay()
    remRelay.getAll()

if __name__=="__main__":
    main()