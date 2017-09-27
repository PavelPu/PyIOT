
from azure.servicebus import ServiceBusService, Message, Queue

print('start')
bus_service = ServiceBusService(service_namespace='PuIOTbus', shared_access_key_name='RootManageSharedAccessKey', shared_access_key_value='SAnp//UKmcm29urWfQy8sdvh3Ipf8/dD7qlN3ZIsWjM=')

#print('send')
#msg = Message(b'Test Message')
#bus_service.send_queue_message('iotqueue', msg)

print('recieve')
msg = bus_service.receive_queue_message('iotqueue', peek_lock=False)

print(msg.body)