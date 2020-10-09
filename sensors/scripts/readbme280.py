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
from bme280 import BME280

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

print("""temperature-and-pressure.py - Displays the temperature and pressure.
Press Ctrl+C to exit!
""")

# Initialise the BMP280
bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

while True:
	# Connect / Reconnect up MQTT
        if not mqtt_connected:
		client.connect(MQTT_SERVER, int(MQTT_PORT), 60)

	# Read in values from BME280 (todo: Look at if we can improve accuracy/use IIR
	temperature = bme280.get_temperature()
	pressure = bme280.get_pressure()
	humidity = bme280.get_humidity()
	print('{:05.2f}*C {:05.2f}hPa {:05.2f}%'.format(temperature, pressure, humidity))

	# Process MQTT messages
        client.loop();

	# Wait a bit
        time.sleep(1)

