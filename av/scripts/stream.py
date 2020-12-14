#!/usr/bin/env python3

import os
import paho.mqtt.client as mqtt

MQTT_SERVER = os.getenv('MQTT_SERVER')
MQTT_PORT = os.getenv('MQTT_PORT')
MQTT_LOGIN = os.getenv('MQTT_LOGIN')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_TOPIC_PREFIX = "BeeHiveMonitor/1/av/"
MQTT_TOPIC_PREFIX_CMD = MQTT_TOPIC_PREFIX + "cmd/"
MQTT_TOPIC_PREFIX_STATE = MQTT_TOPIC_PREFIX + "state/"

mqtt_connected = False;

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global mqtt_connected;
    mqtt_connected = True;
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC_PREFIX_CMD)

def on_disconnect(client, userdata, rc):
    global mqtt_connected;
    mqtt_connected = False;
    print("Disconnected with result code "+str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

if len(MQTT_LOGIN) > 0 and len(MQTT_PASSWORD) > 0:
        client.username_pw_set(MQTT_LOGIN, MQTT_PASSWORD)

while True:
    # Connect / Reconnect up MQTT
    if not mqtt_connected:
        print("Connecting to broker")

        # Set LWT
        client.will_set(MQTT_TOPIC_PREFIX_STATE + "status", "offline", retain=True);
        client.connect(MQTT_SERVER, int(MQTT_PORT), 60)

        # TODO: Check failure here
        while not mqtt_connected:
            client.loop()

        # Send birth certificate
        client.publish(MQTT_TOPIC_PREFIX_STATE + "status", "online", retain=True);

    # Start processing MQTT messages
    client.loop_start();

    # Run FFMPEG
    try:
        os.system("./stream.sh")
    except:
        pass

    # Disconnect
    client.disconnect()
    while mqtt_connected:
      sleep(0.1)
    client.loop_stop()

    # Wait
    sleep(5)

