import time

class TRelay(object):
    num = 0

    def tmet(self):
        print("test method %d" % self.num)
    def __init__(self, n):
        self.num = n

class House(object):
    
    def __init__(self):
        self.startTimeStamp = time.asctime( time.localtime(time.time()))
        self.roomSet = {"bath", "dining", "bedroom"}
        self.relaySet = {
            "bath" : {TRelay(1)},
            "dining" : {TRelay(2)},
            "bedrooom" : {
                TRelay(3), TRelay(4)}
            }

def main():
    house = House()

    print("Hello\n")
    for i in house.relaySet:
        for r in house.relaySet[i]:
            r.tmet()