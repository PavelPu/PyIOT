#!/usr/bin/env python3

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import random
import time
import sys
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue
import config as config
from BME280SensorSimulator import BME280SensorSimulator
import RPi.GPIO as GPIO
#from Adafruit_BME280 import *
import re
#from telemetry import Telemetry
from readDataClass import ReadData
import json
from relays import Relays
from mylogging import Logging
from remoteRelay import RemoteRelay
import subprocess
import urllib.request

# HTTP options
# Because it can poll "after 9 seconds" polls will happen effectively
# at ~10 seconds.
# Note that for scalabilty, the default value of minimumPollingTime
# is 25 minutes. For more information, see:
# https://azure.microsoft.com/documentation/articles/iot-hub-devguide/#messaging
TIMEOUT = 241000
MINIMUM_POLLING_TIME = 9

# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubClient.send_event_async.
# By default, messages do not expire.
MESSAGE_TIMEOUT = 10000

RECEIVE_CONTEXT = 0
MESSAGE_COUNT = 0

TWIN_CONTEXT = 0
SEND_REPORTED_STATE_CONTEXT = 0
METHOD_CONTEXT = 0
TEMPERATURE_ALERT = 30.0

#settings
MESSAGE_SWITCH = False
AUTO_CONTROL = True
AC_MODE = "standby"
BATH_SETPOINT = 1.5
DINING_SETPOINT = -50
BEDROOM_SETPOINT = -50

# global counters
RECEIVE_CALLBACKS = 0
SEND_CALLBACKS = 0
BLOB_CALLBACKS = 0
TWIN_CALLBACKS = 0
SEND_REPORTED_STATE_CALLBACKS = 0
METHOD_CALLBACKS = 0
EVENT_SUCCESS = "success"
EVENT_FAILED = "failed"

# chose HTTP, AMQP or MQTT as transport protocol
PROTOCOL = IoTHubTransportProvider.MQTT

# String containing Hostname, Device Id & Device Key in the format:
# "HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>"
#telemetry = Telemetry()

#if len(sys.argv) < 2:
#    print ( "You need to provide the device connection string as command line arguments." )
#    telemetry.send_telemetry_data(None, EVENT_FAILED, "Device connection string is not provided")
#    sys.exit(0)

def is_correct_connection_string():
    m = re.search("HostName=.*;DeviceId=.*;", CONNECTION_STRING)
    if m:
        return True
    else:
        return False

CONNECTION_STRING = config.CONNECTION_STRING #sys.argv[1]

if not is_correct_connection_string():
    print ( "Device connection string is not correct." )
    #telemetry.send_telemetry_data(None, EVENT_FAILED, "Device connection string is not correct.")
    sys.exit(0)

MSG_TXT = "{\"deviceId\": \"raspPI\",\"dining temperature\": %f,\"bathroom temperature\": %f}"

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(config.GPIO_PIN_ADDRESS, GPIO.OUT)

def readDeviceData (sensors, relays, remoteRelay, logger): 
    global BATH_SETPOINT, DINING_SETPOINT, BEDROOM_SETPOINT, AC_MODE
    sensors.updVal()
    remoteRelay.getAll()
    #sensors.logValues()

    msg_unformatted = {
        "deviceID" : "raspPI",
        "timestamp" : sensors.timeStamp,
        "temperature" : {
            "dining" : sensors.diningTemp,
            "bath" : sensors.bathTemp,
            "bedroom" : remoteRelay.temp,
            "ambient" : sensors.ambTemp
            },
        "relaysState" : {
            "dining" : relays.dining.value,
            "bath" : relays.bath.value,
            "bedroom1": remoteRelay.relay1,
            "bedroom2": remoteRelay.relay2,
            "waterHeater" : relays.waterHeater.value},
        "AutoControl" : AUTO_CONTROL,
        "AutoControlMode" : AC_MODE,
        "setpoints" : {
            "dining" : DINING_SETPOINT,
            "bath" : BATH_SETPOINT,
            "bedroom" : BEDROOM_SETPOINT
            }
        }

    msg_txt_formatted = json.dumps(msg_unformatted)
    logger.logStateString(msg_txt_formatted)

    return msg_txt_formatted


def composeMessage(sensors, relays):

    msg_txt_formatted = readDeviceData(sensors, relays, remoteRelay, logger)

    print (msg_txt_formatted)
    message = IoTHubMessage(msg_txt_formatted)
    # optional: assign ids
    message.message_id = "message_%d" % MESSAGE_COUNT
    message.correlation_id = "correlation_%d" % MESSAGE_COUNT
    # optional: assign properties
    prop_map = message.properties()
    prop_map.add("statusMessage", "true")
    prop_map.add("telemetry", "true")
    return message

def composeStartMessage():
    msg_unformatted = {
        "startTime" : time.asctime( time.localtime(time.time()))
        }
    msg_txt_formatted = json.dumps(msg_unformatted)
    message = IoTHubMessage(msg_txt_formatted)
    # optional: assign ids
    message.message_id = "message_%d" % MESSAGE_COUNT
    message.correlation_id = "correlation_%d" % MESSAGE_COUNT
    # optional: assign properties
    prop_map = message.properties()
    prop_map.add("startupMessage", "true")
    prop_map.add("telemetry", "false")
    return message

def receive_message_callback(message, counter):
    global RECEIVE_CALLBACKS
    message_buffer = message.get_bytearray()
    size = len(message_buffer)
    print ( "Received Message [%d]:" % counter )
    print ( "    Data: <<<%s>>> & Size=%d" % (message_buffer[:size].decode("utf-8"), size) )
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: %s" % key_value_pair )
    counter += 1
    RECEIVE_CALLBACKS += 1
    print ( "    Total calls received: %d" % RECEIVE_CALLBACKS )
    return IoTHubMessageDispositionResult.ACCEPTED


def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    print ( "Confirmation[%d] received for message with result = %s" % (user_context, result) )
    map_properties = message.properties()
    print ( "    message_id: %s" % message.message_id )
    print ( "    correlation_id: %s" % message.correlation_id )
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: %s" % key_value_pair )
    SEND_CALLBACKS += 1
    print ( "    Total calls confirmed: %d" % SEND_CALLBACKS )
    #led_blink()


def device_twin_callback(update_state, payload, user_context):
    global TWIN_CALLBACKS, AUTO_CONTROL, BATH_SETPOINT, DINING_SETPOINT, BEDROOM_SETPOINT, AC_MODE, MESSAGE_SWITCH
    print ( "\nTwin callback called with:\nupdateStatus = %s\npayload = %s\ncontext = %s" % (update_state, payload, user_context) )
    TWIN_CALLBACKS += 1
    twin = json.loads(payload)
    if 'desired' in twin:
        AUTO_CONTROL = twin["desired"]["autoControl"]["enabled"]
        AC_MODE = twin["desired"]["autoControl"]["mode"]
        BATH_SETPOINT = twin["desired"]["autoControl"]["setpoints"][AC_MODE]["bath"]
        DINING_SETPOINT = twin["desired"]["autoControl"]["setpoints"][AC_MODE]["dining"]
        BEDROOM_SETPOINT = twin["desired"]["autoControl"]["setpoints"][AC_MODE]["bedroom"]
        MESSAGE_SWITCH = twin["desired"]["sendTelemetry"]
    if 'autoControl' in twin:
        AUTO_CONTROL = twin["autoControl"]["enabled"]
        AC_MODE = twin["autoControl"]["mode"]
        BATH_SETPOINT = twin["autoControl"]["setpoints"][AC_MODE]["bath"]
        DINING_SETPOINT = twin["autoControl"]["setpoints"][AC_MODE]["dining"]
        BEDROOM_SETPOINT = twin["autoControl"]["setpoints"][AC_MODE]["bedroom"]
        MESSAGE_SWITCH = twin["sendTelemetry"]
    #if update_state == "PARTIAL":
    #    AUTO_CONTROL = twin["autoControl"]["enabled"]
    #else:
    #    AUTO_CONTROL = twin["desired"]["autoControl"]["enabled"]
    #print("Property parsed from device twin " + twin["desired"]["autoControl"])
    print ( "Total calls confirmed: %d\n" % TWIN_CALLBACKS )


def send_reported_state_callback(status_code, user_context):
    global SEND_REPORTED_STATE_CALLBACKS
    print ( "Confirmation for reported state received with:\nstatus_code = [%d]\ncontext = %s" % (status_code, user_context) )
    SEND_REPORTED_STATE_CALLBACKS += 1
    print ( "    Total calls confirmed: %d" % SEND_REPORTED_STATE_CALLBACKS )


def device_method_callback(method_name, payload, user_context):
    global METHOD_CALLBACKS,MESSAGE_SWITCH, MESSAGE_COUNT, sensor, relays, logger, remoteRelay, AC_MODE
    print ( "\nMethod callback called with:\nmethodName = %s\npayload = %s\ncontext = %s" % (method_name, payload, user_context) )
    METHOD_CALLBACKS += 1
    print ( "Total calls confirmed: %d\n" % METHOD_CALLBACKS )
    device_method_return_value = DeviceMethodReturnValue()
    device_method_return_value.response = "{ \"Response\": \"This is the response from the device\" }"
    device_method_return_value.status = 200
    if method_name == "start":
        MESSAGE_SWITCH = True
        print ( "Start sending message\n" )
        device_method_return_value.response = "{ \"Response\": \"Successfully started\" }"
        return device_method_return_value
    if method_name == "stop":
        MESSAGE_SWITCH = False
        print ( "Stop sending message\n" )
        device_method_return_value.response = "{ \"Response\": \"Successfully stopped\" }"
        return device_method_return_value
    if method_name == "setACmode":
        if 'mode' in payload:
            if payload['mode'] == "standby":
                AC_MODE = "standby"
            if payload['mode'] == "operating":
                AC_MODE == "operating"
            statusText = readDeviceData(sensor, relays, remoteRelay, logger) 
            device_method_return_value.response = statusText
        else: 
            device_method_return_value.response = "{ \"Response\": \"Mode change unsuccessful, bad payload\" }"
        return device_method_return_value
    
    if method_name == "modeSTB":
        AC_MODE = "standby"
        statusText = readDeviceData(sensor, relays, remoteRelay, logger) 
        device_method_return_value.response = statusText
        return device_method_return_value
    
    if method_name == "modeOPR":
        AC_MODE = "operating"
        statusText = readDeviceData(sensor, relays, remoteRelay, logger) 
        device_method_return_value.response = statusText
        return device_method_return_value

    if method_name == "send":
        print ("Sending message")
        message = composeMessage(sensor,relays)
        client.send_event_async(message, send_confirmation_callback, MESSAGE_COUNT)
        print ( "IoTHubClient.send_event_async accepted message [%d] for transmission to IoT Hub." % MESSAGE_COUNT )
        status = client.get_send_status()
        print ( "Send status: %s" % status )
        MESSAGE_COUNT += 1
        device_method_return_value.response = "{ \"Response\": \"Message sent\" }"
    if method_name == "status":
        statusText = readDeviceData(sensor, relays, remoteRelay, logger)
        device_method_return_value.response = statusText
    if method_name == "heatOn":
        print("Switching heating ON")
        relays.dining.on()
        relays.bath.on()
        remoteRelay.relay1On()
        remoteRelay.relay2On()
        statusText = readDeviceData(sensor, relays, remoteRelay, logger)
        device_method_return_value.response = statusText
    if method_name == "heatOff":
        print("Switching heating OFF")
        relays.dining.off()
        relays.bath.off()
        remoteRelay.relay1Off()
        remoteRelay.relay2Off()
        statusText = readDeviceData(sensor, relays, remoteRelay, logger)
        device_method_return_value.response = statusText
    if method_name == "waterOn":
        print("Switching water heating ON")
        relays.waterHeater.on()
        statusText = readDeviceData(sensor, relays, remoteRelay, logger)
        device_method_return_value.response = statusText
    if method_name == "waterOff":
        print("Switching water heating OFF")
        relays.waterHeater.off()
        statusText = readDeviceData(sensor, relays, remoteRelay, logger)
        device_method_return_value.response = statusText
    if method_name == "update":
        subprocess.call("/home/pi/PyIOT/update.sh")
        device_method_return_value.response = "{ \"Response\": \"Updating\" }"
    return device_method_return_value


def blob_upload_conf_callback(result, user_context):
    global BLOB_CALLBACKS
    print ( "Blob upload confirmation[%d] received for message with result = %s" % (user_context, result) )
    BLOB_CALLBACKS += 1
    print ( "    Total calls confirmed: %d" % BLOB_CALLBACKS )


def iothub_client_init():
    # prepare iothub client
    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
    if client.protocol == IoTHubTransportProvider.HTTP:
        client.set_option("timeout", TIMEOUT)
        client.set_option("MinimumPollingTime", MINIMUM_POLLING_TIME)
    # set the time until a message times out
    client.set_option("messageTimeout", MESSAGE_TIMEOUT)
    # to enable MQTT logging set to 1
    if client.protocol == IoTHubTransportProvider.MQTT:
        client.set_option("logtrace", 0)
    client.set_message_callback(
        receive_message_callback, RECEIVE_CONTEXT)
    if client.protocol == IoTHubTransportProvider.MQTT or client.protocol == IoTHubTransportProvider.MQTT_WS:
        client.set_device_twin_callback(
            device_twin_callback, TWIN_CONTEXT)
        client.set_device_method_callback(
            device_method_callback, METHOD_CONTEXT)
    return client


def print_last_message_time(client):
    try:
        last_message = client.get_last_message_receive_time()
        print ( "Last Message: %s" % time.asctime(time.localtime(last_message)) )
        print ( "Actual time : %s" % time.asctime() )
    except IoTHubClientError as iothub_client_error:
        if iothub_client_error.args[0].result == IoTHubClientResult.INDEFINITE_TIME:
            print ( "No message received" )
        else:
            print ( iothub_client_error )

def reportState(relays): #report state to device twin
    global DINING_SETPOINT, BATH_SETPOINT 
    deivceState = {
        "relaysState": {
            "dining" : relays.dining.value,
            "bath" : relays.bath.value
            },
        "setpoints" : {
            "dining" : DINING_SETPOINT,
            "bath" : BATH_SETPOINT
            }
        }
    deviceStateJson = json.dumps(deivceState)
    client.send_reported_state(deviceStateJson, len(deviceStateJson), send_reported_state_callback, SEND_REPORTED_STATE_CONTEXT)

def autoControl():
    global sensor, relays, remoteRelay, BATH_SETPOINT, DINING_SETPOINT, BEDROOM_SETPOINT

    if sensor.bathTemp < BATH_SETPOINT:
        relays.bath.on()
        try:
            response = urllib.request.urlopen("%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=On" % (config.DOMOTICZ_ADDRESS, config.IDX_BATH))
        except:
            print("unable to talk to Domoticz")
        #print( "Turning heating in bathroom ON")
    if sensor.bathTemp >= BATH_SETPOINT + 1:
        relays.bath.off()
        try:
            response = urllib.request.urlopen("%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=Off" % (config.DOMOTICZ_ADDRESS, config.IDX_BATH))
        except:
            print("unable to talk to Domoticz")
        #print( "Turning heating in bathroom OFF")

    if sensor.bathTemp < 1.5:
        relays.waterHeater.on()
        try:
            response = urllib.request.urlopen("%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=On" % (config.DOMOTICZ_ADDRESS, config.IDX_WH))
        except:
            print("unable to talk to Domoticz")
        #print( "Turning heating in bathroom ON")
    if sensor.bathTemp >= BATH_SETPOINT + 1:
        relays.bath.off()
        try:
            response = urllib.request.urlopen("%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=Off" % (config.DOMOTICZ_ADDRESS, config.IDX_WH))
        except:
            print("unable to talk to Domoticz")
        #print( "Turning heating in bathroom OFF")

    if sensor.diningTemp < DINING_SETPOINT:
        relays.dining.on()
        try:
            response = urllib.request.urlopen("%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=On" % (config.DOMOTICZ_ADDRESS, config.IDX_DINING))
        except:
            print("unable to talk to Domoticz")
        #print( "Turning heating in dining room ON")
    if sensor.diningTemp >= DINING_SETPOINT + 1:
        relays.dining.off()
        try:
            response = urllib.request.urlopen("%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=Off" % (config.DOMOTICZ_ADDRESS, config.IDX_DINING))
        except:
            print("unable to talk to Domoticz")
       
        #print( "Turning heating in dining room OFF")

    if remoteRelay.temp < BEDROOM_SETPOINT:
        remoteRelay.relay1On()
        remoteRelay.relay2On()
        try:
            response = urllib.request.urlopen("%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=On" % (config.DOMOTICZ_ADDRESS, config.IDX_BED1))
            response = urllib.request.urlopen("%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=On" % (config.DOMOTICZ_ADDRESS, config.IDX_BED2))
        except:
            print("unable to talk to Domoticz")
    if remoteRelay.temp >= BEDROOM_SETPOINT + 1:
        remoteRelay.relay1Off()
        remoteRelay.relay2Off()
        try:
            response = urllib.request.urlopen("%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=Off" % (config.DOMOTICZ_ADDRESS, config.IDX_BED1))
            response = urllib.request.urlopen("%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=Off" % (config.DOMOTICZ_ADDRESS, config.IDX_BED2))
        except:
            print("unable to talk to Domoticz")

def iothub_client_sample_run():
    try:
        global client, sensor, relays, logger, remoteRelay, MESSAGE_COUNT
        client = iothub_client_init()

        logger = Logging()
        sensor = ReadData()
        relays = Relays()
        remoteRelay = RemoteRelay()

        if client.protocol == IoTHubTransportProvider.MQTT:
            print ( "IoTHubClient is reporting state" )
            #reported_state = "{\"newState\":\"standBy\",\"relaysState\":{\"dining\":\"off\"}}"
            #client.send_reported_state(reported_state, len(reported_state), send_reported_state_callback, SEND_REPORTED_STATE_CONTEXT)
            reportState(relays)
        message = composeStartMessage()
        client.send_event_async(message, send_confirmation_callback, MESSAGE_COUNT)
        print ( "IoTHubClient.send_event_async accepted message [%d] for transmission to IoT Hub." % MESSAGE_COUNT )

        status = client.get_send_status()
        print ( "Send status: %s" % status )
        MESSAGE_COUNT += 1
        
        #telemetry.send_telemetry_data(parse_iot_hub_name(), EVENT_SUCCESS, "IoT hub connection is established")
        while True:
            global MESSAGE_SWITCH
            if MESSAGE_SWITCH:
                # send a few messages every minute
                print ( "IoTHubClient sending %d messages" % MESSAGE_COUNT )
                
                message = composeMessage(sensor,relays)
                client.send_event_async(message, send_confirmation_callback, MESSAGE_COUNT)
                print ( "IoTHubClient.send_event_async accepted message [%d] for transmission to IoT Hub." % MESSAGE_COUNT )

                status = client.get_send_status()
                print ( "Send status: %s" % status )
                MESSAGE_COUNT += 1
            
            #log current state
            statusText = readDeviceData(sensor, relays, remoteRelay, logger)

            if AUTO_CONTROL:
                autoControl()
            time.sleep(config.MESSAGE_TIMESPAN / 1000.0)

    except IoTHubError as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )
        #telemetry.send_telemetry_data(parse_iot_hub_name(), EVENT_FAILED, "Unexpected error %s from IoTHub" % iothub_error)
        return
    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )

    print_last_message_time(client)

#def led_blink():
#    GPIO.output(config.GPIO_PIN_ADDRESS, GPIO.HIGH)
#    time.sleep(config.BLINK_TIMESPAN / 1000.0)
#    GPIO.output(config.GPIO_PIN_ADDRESS, GPIO.LOW)

def usage():
    print ( "Usage: iothub_client_sample.py -p <protocol> -c <connectionstring>" )
    print ( "    protocol        : <amqp, amqp_ws, http, mqtt, mqtt_ws>" )
    print ( "    connectionstring: <HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>>" )

def parse_iot_hub_name():
    m = re.search("HostName=(.*?)\.", CONNECTION_STRING)
    return m.group(1)

if __name__ == "__main__":
    print ( "\nPython %s" % sys.version )
    print ( "IoT Hub Client for Python" )

    iothub_client_sample_run()
