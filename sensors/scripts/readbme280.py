#!/usr/bin/env python3
import os
import paho.mqtt.client as mqtt

#
# Support routines
#

# Gets the CPU temperature in degrees C

from subprocess import PIPE, Popen

def get_cpu_temperature():
	process = Popen(['/opt/vc/bin/vcgencmd', 'measure_temp'], stdout=PIPE)
	output, _error = process.communicate()
	return float(output[output.index('=') + 1:output.rindex("'")])

# ------------------------------

#
# MQTT Setup
#

MQTT_SERVER = os.getenv('MQTT_SERVER')
MQTT_PORT = os.getenv('MQTT_PORT')
MQTT_LOGIN = os.getenv('MQTT_LOGIN')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_TOPIC_PREFIX = "BeeHiveMonitor/1/"
MQTT_TOPIC_PREFIX_STATE = MQTT_TOPIC_PREFIX + "state/"

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

#
# BME280 setup
#

import time
from bme280 import BME280

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

print("""temperature-and-pressure.py - Displays the temperature and pressure.
Press Ctrl+C to exit!
""")

# Initialise the BME280
bus = SMBus(1)
bme280 = BME280(i2c_dev=bus, i2c_addr=0x77)

factor = 1.2  # Smaller numbers adjust temp down, vice versa
smooth_size = 10  # Dampens jitter due to rapid CPU temp changes
cpu_temps = []

while True:
	# Connect / Reconnect up MQTT
	if not mqtt_connected:
		client.connect(MQTT_SERVER, int(MQTT_PORT), 60)

	# Read in values from BME280 (todo: Look at if we can improve accuracy/use IIR
	cpu_temp = get_cpu_temperature()
	cpu_temps.append(cpu_temp)

	if len(cpu_temps) > smooth_size:
        	cpu_temps = cpu_temps[1:]

	smoothed_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
	raw_temperature = bme280.get_temperature()
	comp_temp = raw_temp - ((smoothed_cpu_temp - raw_temp) / factor)

	pressure = bme280.get_pressure()
	humidity = bme280.get_humidity()
	print('Temp: {:05.2f}*C Compensated Temp: {:05.2f}*C Pressure: {:05.2f}hPa Relative Humidity: {:05.2f}%'.format(raw_temperature, comp_temp, pressure, humidity))

	client.publish(MQTT_TOPIC_PREFIX_STATE + "temperature", raw_temperature);
	client.publish(MQTT_TOPIC_PREFIX_STATE + "comensated_temperature", comp_temp);
	client.publish(MQTT_TOPIC_PREFIX_STATE + "pressure", pressure);
	client.publish(MQTT_TOPIC_PREFIX_STATE + "relativehumidity", humidity);

	# Process MQTT messages
	client.loop();

	# Wait a bit
	time.sleep(1)
