#!/usr/bin/env python

# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

import os, json, time
from datetime import datetime


def customCallback(payload, responseStatus, token):
    print('responseStatus={}'.format(responseStatus))
    if responseStatus=='accepted':
        print("got accepted")
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("property: " + str(payloadDict["state"]["desired"]["property"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "timeout":
        print("Update request " + token + " time out!")
    # if responseStatus == "accepted":
    #     pirnt("got accepted")
    #     payloadDict = json.loads(payload)
    #     print("~~~~~~~~~~~~~~~~~~~~~~~")
    #     print("Update request with token: " + token + " accepted!")
    #     print("property: " + str(payloadDict["state"]["desired"]["property"]))
    #     print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")
    

if 'IOT_CLIENT_ID' in os.environ:
    myShadowClient = AWSIoTMQTTShadowClient(os.environ['IOT_CLIENT_ID'])
    clientId = os.environ['IOT_CLIENT_ID']
else:
    print("missing IOT_CLIENT_ID in environment variables")


if 'IOT_ENDPOINT' in os.environ:
    myShadowClient.configureEndpoint(os.environ['IOT_ENDPOINT'], 8883)
else:
    print("missing IOT_ENDPOINT in environment variables")
    
if 'IOT_ROOT_CA_PATH' in os.environ and 'IOT_PRIVATE_KEY_PATH' in os.environ and 'IOT_CERT_PATH' in os.environ:
    myShadowClient.configureCredentials(os.environ['IOT_ROOT_CA_PATH'], os.environ['IOT_PRIVATE_KEY_PATH'], os.environ['IOT_CERT_PATH'])    
else:
    print("missing IoT credentials")

# For certificate based connection
# myMQTTClient = AWSIoTMQTTClient("myClientID")
# # For Websocket connection
# # myMQTTClient = AWSIoTMQTTClient("myClientID", useWebsocket=True)
# # Configurations
# # For TLS mutual authentication
# myMQTTClient.configureEndpoint("YOUR.ENDPOINT", 8883)
# # For Websocket
# # myMQTTClient.configureEndpoint("YOUR.ENDPOINT", 443)
# myMQTTClient.configureCredentials("YOUR/ROOT/CA/PATH", "PRIVATE/KEY/PATH", "CERTIFICATE/PATH")
# For Websocket, we only need to configure the root CA
# myMQTTClient.configureCredentials("YOUR/ROOT/CA/PATH")

myMQTTClient = myShadowClient.getMQTTConnection()

myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(10)  # 10 sec

myMQTTClient.connect()
myMQTTClient.publish("{}/update".format(clientId), '{"foo":"bar"}', 0)
print('message published to {}/update'.format(clientId))
# myMQTTClient.subscribe("myTopic", 1, customCallback)
# myMQTTClient.unsubscribe("myTopic")
myMQTTClient.disconnect()
print('disconnected')


#
# update shadow
#

myShadowClient.connect()
# # Create a device shadow instance using persistent subscription
myDeviceShadow = myShadowClient.createShadowHandlerWithName("{}".format(os.environ['IOT_CLIENT_ID']), True)
# # Shadow operations
#myDeviceShadow.shadowGet(customCallback, 5)
# now = datetime.now()
# JSONPayload = '{"state":{"desired":{"property":"'+ str(now) +'"}}}'
# myDeviceShadow.shadowUpdate(JSONPayload, customCallback, 5)
# myDeviceShadow.shadowDelete(customCallback, 5)
# myDeviceShadow.shadowRegisterDeltaCallback(customCallback)
# myDeviceShadow.shadowUnregisterDeltaCallback()
# myShadowClient.disconnect()

while True:
    now = datetime.now()
    JSONPayload = '{"state":{"desired":{"property":"'+ str(now) +'"}}}'
    myDeviceShadow.shadowUpdate(JSONPayload, customCallback, 5)
    time.sleep(1)

