#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: MIT 2.009 Purple Team
# Date: November 20, 2019

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json


topic = 'demo-topic'
loopCount = 0


# For certificate based connection
myMQTTClient = AWSIoTMQTTClient("Triton")
# For Websocket connection
# myMQTTClient = AWSIoTMQTTClient("myClientID", useWebsocket=True)
# Configurations
# For TLS mutual authentication
myMQTTClient.configureEndpoint("a2rpq57lrt0k72-ats.iot.us-east-2.amazonaws.com", 8883)
# For Websocket
# myMQTTClient.configureEndpoint("YOUR.ENDPOINT", 443)
# For TLS mutual authentication with TLS ALPN extension
# myMQTTClient.configureEndpoint("YOUR.ENDPOINT", 443)
myMQTTClient.configureCredentials("/usr/local/share/ca-certificates/aws.crt", "/home/purple/26b644023d-private.pem.key", "/home/purple/26b644023d-certificate.pem.crt")
# For Websocket, we only need to configure the root CA
# myMQTTClient.configureCredentials("YOUR/ROOT/CA/PATH")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
def payload_report(self, params, packet):
	print('Message:', packet.payload)
myMQTTClient.subscribe('demo-test-write', 1, payload_report)


i = 0
while True:
	i = i+1
	print('Publishing to demo-test:', i)
	myMQTTClient.publish('test/date', i, 0)
	time.sleep(5)




