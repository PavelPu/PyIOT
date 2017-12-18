import socket
import netifaces as ni
import json, urllib.request

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
            try:
                dom_address = "http://127.0.0.1:8181"
                dev_id = 12
                response = urllib.request.urlopen("%s/json.htm?type=command&param=udevice&idx=%s&nvalue=0&svalue=%s" % (dom_address, dev_id, self.temp))
                device_data = json.loads(response.read().decode('utf-8'))
                #resp = device_data['result'][0]['Temp']
            except Exception:
                amb_temp = "NA"

    def relay1On (self):
        self.getAll()
        iter = 0
        while (self.relay1 != True):
            iter = iter + 1
            if (iter > 5):
                self.relay1 = "NA"
                break
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
        self.getAll()
        iter = 0
        while (self.relay1 != False):
            iter = iter + 1
            if (iter > 5):
                self.relay1 = "NA"
                break
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
        self.getAll()
        iter = 0
        while (self.relay2 != True):
            iter = iter + 1
            if (iter > 5):
                self.relay2 = "NA"
                break        
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
                self.relay2 = "NA"

    def relay2Off (self):
        self.getAll()
        iter = 0
        while (self.relay2 != False):
            iter = iter + 1
            if (iter > 5):
                self.relay2 = "NA"
                break
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
                self.relay2 = "NA"



    def __init__(self):
        
        self.UDP_IP = "192.168.8.100"
        
        self.UDP_PORT = 7777
        try:
            self.UDP_LIP = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
            self.sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
            self.sock.settimeout(1)
            self.sock.bind((self.UDP_LIP, self.UDP_PORT))
            self.getAll()
        except:
            self.temp = "NA"
            self.relay1 = "NA"
            self.relay2 = "NA"

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