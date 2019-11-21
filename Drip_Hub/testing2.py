#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: MIT 2.009 Purple Team
# Date: November 20, 2019

from __future__ import print_function
import sys
import ssl
import time
import datetime
import logging, traceback
import paho.mqtt.client as mqtt

IoT_protocol_name = "Triton"
aws_iot_endpoint = "a2rpq57lrt0k72-ats.iot.us-east-2.amazonaws.com" # <random>.iot.<region>.amazonaws.com
url = "https://{}".format(aws_iot_endpoint)

ca = "/usr/local/share/ca-certificates/aws3.crt" 
private = "/home/purple/26b644023d-private.pem.key"
cert = "/home/purple/26b644023d-certificate.pem.crt"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(log_format)
logger.addHandler(handler)

def ssl_alpn():

    #debug print opnessl version
    logger.info("open ssl version:{}".format(ssl.OPENSSL_VERSION))
    ssl_context = ssl.create_default_context()
    ssl_context.set_alpn_protocols([IoT_protocol_name])
    ssl_context.load_verify_locations(cafile=ca)
    ssl_context.load_cert_chain(certfile=cert, keyfile=private)

    return  ssl_context

def messageDecoder(self, client, userdata, msg):
    message = msg.payload.decode(encoding='UTF-8')
    logger.info('Message:', message)

if __name__ == '__main__':
    topic = "test/date"

    mqttc = mqtt.Client()
    ssl_context= ssl_alpn()
    mqttc.tls_set_context(context=ssl_context)
    logger.info("start connect")
    mqttc.connect(aws_iot_endpoint, port=8883)
    logger.info("connect success")
    mqttc.on_messgae = messageDecoder
    mqttc.subscribe('test/write')
    mqttc.loop_start()
	
    while True:
        now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        logger.info("try to publish:{}".format(now))
        mqttc.publish(topic, now)
        time.sleep(1)

    


