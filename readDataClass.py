#!/usr/bin/env python3

import time, json, urllib.request
#import , logging, urllib3, requests

base_dir = '/sys/bus/w1/devices/'

#device_names = ['28-051700f1d8ff', '28-051700f63cff']

#device_folders = ['/sys/bus/w1/devices/28-051700f1d8ff', '/sys/bus/w1/devices/28-051700f63cff']
# /sys/bus/w1/devices/28-051700f63cff


device_files = ['/sys/bus/w1/devices/28-051700f1d8ff/w1_slave', '/sys/bus/w1/devices/28-051700f63cff/w1_slave'] 

class ReadData: 

    
    def readWeather(self):

        dom_address = "http://127.0.0.1:8181"
        dev_id = 5
        response = urllib.request.urlopen("%s/json.htm?type=devices&rid=%s" % (dom_address, dev_id))
        #str = urllib3.request("%s/json.htm?type=devices&rid=%s" % (dom_address, dev_id), timeout=5)
        #r = requests.get("%s/json.htm?type=devices&rid=%s" % (dom_address, dev_id))
        #device_data = r.json()#json.loads(r)
        #amb_temp = device_data['result'][0]['Temp']
        device_data = json.loads(response.read().decode('utf-8'))
        amb_temp = device_data['result'][0]['Temp']

        return amb_temp
 
    def read_temp_raw(self, dev_file):
        f = open(dev_file, 'r')
        lines = f.readlines()
        f.close()
        return lines
    
    def read_temp(self, dev_file):
        
        lines = self.read_temp_raw(dev_file)
        # Analyze if the last 3 characters are 'YES'.
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw(dev_file)
        # Find the index of 't=' in a string.
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            # Read the temperature .
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0

            return temp_c
    
    def updVal(self):
        self.diningTemp = self.read_temp(device_files[1])
        self.bathTemp = self.read_temp(device_files[0])
        self.timeStamp = time.asctime( time.localtime(time.time()))
        self.ambTemp = self.readWeather()

    def logValues(self):
        self._dt = time.strftime("%d %b %Y", time.localtime(time.time()))
        self._logname = '/home/pi/PyIOT/logs/' + self._dt +'_log.txt'
        self._logfile = open(self._logname, 'a')
        self._logString = self.timeStamp+ ";" + str(self.diningTemp) + ";" + str(self.bathTemp) + ";" + str(self.ambTemp) + "\n" 
        self._logfile.write(self._logString)
        self._logfile.close()

    def __init__(self):
        self.diningTemp = self.read_temp(device_files[1])
        self.bathTemp = self.read_temp(device_files[0])
        self.timeStamp = time.asctime( time.localtime(time.time()))
        self.ambTemp = self.readWeather()

def main():


    sensors = ReadData()

    print ("Local current time :", sensors.timeStamp)

    temp = sensors.diningTemp
    temp2 = sensors.bathTemp
    
    print (sensors.timeStamp, "\ttemp:", temp, "\ttemp2:", temp2, "\tamb:", sensors.ambTemp)

    #sensors.logValues()

if __name__=="__main__":
    main()
