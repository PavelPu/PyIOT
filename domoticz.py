

import sys, json, urllib2


def readWeather:

    adress = "192.168.8.100:8181"
    dev_id = 5
    device_data = json.load(urllib2.urlopen("%s/json.htm?type=devices&rid=%s" % (adress, dev_id), timeout=5))
    amb_temp = device_data['result'][0]['Temp']

    return amb_temp
