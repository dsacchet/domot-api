#!/usr/bin/python3

import paho.mqtt.client as mqtt
import math
import socket
import configparser

config = configparser.ConfigParser()

try:
    config.read("/var/www/conf/oh2mqttpersistence2graphite.ini")
    broker_username=config.get('broker','username')
    broker_password=config.get('broker','password')
    broker_topic=config.get('broker','topic')
    graphite_host=config.get('graphite','host')
    graphite_port=int(config.get('graphite','port'))
except:
    print("Unable to read configuration file or missing configuration entries")
    sys.exit(1)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(broker_topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    message=msg.payload.decode().split('|')
    timestamp=math.floor(float(str(message[3]))/1000)-math.floor(float(message[3])/1000)%60
    value=float(message[2])
    message='%s %.1f %d\n'%(message[1],value,timestamp)
    sock = socket.socket()
    sock.connect((graphite_host,graphite_port))
    sock.sendall(message.encode())
    sock.close()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(broker_username,broker_password)
client.connect("localhost", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
