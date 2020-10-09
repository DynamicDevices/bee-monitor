#!/usr/bin/env python3
import os
import paho.mqtt.client as mqtt

MQTT_SERVER = os.getenv('MQTT_SERVER')
MQTT_PORT = os.getenv('MQTT_PORT')
MQTT_LOGIN = os.getenv('MQTT_LOGIN')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD') 

mqtt_connected = False;

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    mqtt_connected = True;
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

def on_disconnect(client, userdata, rc):
    mqtt_connected = False;
    print("Disconnected with result code "+str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.username_pw_set(MQTT_LOGIN, MQTT_PASSWORD)

import time
from bmp280 import BMP280

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

print("""temperature-and-pressure.py - Displays the temperature and pressure.
Press Ctrl+C to exit!
""")

# Initialise the BMP280
bus = SMBus(1)
bmp280 = BMP280(i2c_dev=bus, i2c_addr=0x77)

while True:
        if not mqtt_connected:
                client.connect(MQTT_SERVER, int(MQTT_PORT), 60)

        temperature = bmp280.get_temperature()
        pressure = bmp280.get_pressure()
        print('{:05.2f}*C {:05.2f}hPa'.format(temperature, pressure))
        time.sleep(1)

        client.loop();

