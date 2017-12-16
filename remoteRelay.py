import socket

class RemoteRelay:
    def getAll (self):
        rcv = False
        iter = 0
        while (rcv == False):
            iter = iter + 1
            if (iter > 5):
                self.relay1 = "NA"
                self.relay2 = "NA"
                self.temp = "NA"
                break
            self.sock.sendto(bytes("!GetAll\r", "ascii"), (self.UDP_IP, self.UDP_PORT))
            try:
                data, server = self.sock.recvfrom(1024)
                ans = data.decode("ascii").split("\r")
                print(ans)
                if (len(ans) == 9):
                    rcv = True
                    if (ans[0] == "!LEDOFF1"):
                        self.relay1 = False
                    elif (ans[0] == "!LEDON1"):
                        self.relay1 = True
                    else: 
                        self.relay1 = "NA"

                    if (ans[1] == "!LEDOFF2"):
                        self.relay2 = False
                    elif (ans[1] == "!LEDON2"):
                        self.relay2 = True
                    else: 
                        self.relay2 = "NA"

                    if (ans[5].find("+") > 0):
                        self.temp = int(ans[5][ans[5].find("+")+1:])
                    elif (ans[5].find("-") > 0):
                        self.temp = int(ans[5][ans[5].find("-")+1:])
                    else:
                        self.temp = "NA"
            except:
                print("bad responce reading all")


    def relay1On (self):
        self.getAll()
        self.sock.sendto(bytes("!SetR1_1\r", "ascii"), (self.UDP_IP, self.UDP_PORT))
        try:
            data, server = self.sock.recvfrom(1024)
            ans = data.decode("ascii").split("\r")
            print(len(ans))
            if (len(ans) == 2):
                if (ans[0] == "!LEDOFF1"):
                    self.relay1 = False
                elif (ans[1] == "!LEDON1"):
                    self.relay1 = True
                else: 
                    self.relay1 = "NA"
        except:
            self.relay1 = "NA"
        
    def relay1Off (self):
        self.sock.sendto(bytes("!SetR0_1\r", "ascii"), (self.UDP_IP, self.UDP_PORT))
        try:
            data, server = self.sock.recvfrom(1024)
            ans = data.decode("ascii").split("\r")
            print(len(ans))
            if (len(ans) == 2):
                if (ans[0] == "!LEDOFF1"):
                    self.relay1 = False
                elif (ans[0] == "!LEDON1"):
                    self.relay1 = True
                else: 
                    self.relay1 = "NA"
        except:
            self.relay1 = "NA"
            
            
    def relay2On (self):
        self.sock.sendto(bytes("!SetR1_2\r", "ascii"), (self.UDP_IP, self.UDP_PORT))
        try:
            data, server = self.sock.recvfrom(1024)
            ans = data.decode("ascii").split("\r")
            print(len(ans))
            if (len(ans) == 2):
                if (ans[0] == "!LEDOFF2"):
                    self.relay2 = False
                elif (ans[0] == "!LEDON2"):
                    self.relay2 = True
                else: 
                    self.relay2 = "NA"
        except:
            self.relay1 = "NA"

    def relay2Off (self):
        self.sock.sendto(bytes("!SetR0_2\r", "ascii"), (self.UDP_IP, self.UDP_PORT))
        try:
            data, server = self.sock.recvfrom(1024)
            ans = data.decode("ascii").split("\r")
            print(len(ans))
            if (len(ans) == 2):
                if (ans[0] == "!LEDOFF2"):
                    self.relay2 = False
                elif (ans[0] == "!LEDON2"):
                    self.relay2 = True
                else: 
                    self.relay2 = "NA"
        except:
            self.relay1 = "NA"



    def __init__(self):
        self.UDP_IP = "192.168.8.100"
        self.UDP_LIP = "192.168.8.104"
        self.UDP_PORT = 7777
        self.sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        self.sock.settimeout(1)
        self.sock.bind((self.UDP_LIP, self.UDP_PORT))
        self.getAll()

def main():

    remRelay = RemoteRelay()
    #remRelay.sock = socket.socket(socket.AF_INET, # Internet
    #                 socket.SOCK_DGRAM) # UDP
    #remRelay.sock.settimeout(1)
    #remRelay.sock.bind((remRelay.UDP_LIP, remRelay.UDP_PORT))
    #remRelay.sock.sendto(bytes(MESSAGE_GET,"ascii"), ("192.168.8.100", 7777))
    #remRelay.getAll()
    print(remRelay.relay1)
    #remRelay.relay1Off()

    print(remRelay.relay2)
    print(remRelay.temp)


if __name__=="__main__":
    main()