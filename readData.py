#!/usr/bin/env python

import os
import glob
import time

base_dir = '/sys/bus/w1/devices/'

#device_names = ['28-051700f1d8ff', '28-051700f63cff']

#device_folders = ['/sys/bus/w1/devices/28-051700f1d8ff', '/sys/bus/w1/devices/28-051700f63cff']
# /sys/bus/w1/devices/28-051700f63cff


device_files = ['/sys/bus/w1/devices/28-051700f1d8ff/w1_slave', '/sys/bus/w1/devices/28-051700f63cff/w1_slave'] 

 
def read_temp_raw(dev_file):
    f = open(dev_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp(dev_file):
    
    lines = read_temp_raw(dev_file)
    # Analyze if the last 3 characters are 'YES'.
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(dev_file)
    # Find the index of 't=' in a string.
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        # Read the temperature .
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0

        return temp_c

def main():


    localtime = time.asctime( time.localtime(time.time()) )
    print ("Local current time :", localtime)

    temp = read_temp(device_files[0])
    temp2 = read_temp(device_files[1])
    
    print (localtime, "\ttemp:", temp, "\ttemp2:", temp2)

    dt = time.strftime("%d %b %Y", time.localtime(time.time()))
    logname = '/home/pi/PyIOT/logs/' + dt +'_log.txt'

    logfile = open(logname, 'a')

    string = localtime + ";" + str(temp) + ";" + str(temp2) + "\n"
    #print(string)
    
    logfile.write(string)
    
    logfile.close()

if __name__=="__main__":
    main()
