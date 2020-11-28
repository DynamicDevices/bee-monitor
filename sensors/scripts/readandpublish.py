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
	output = output.decode('utf-8')
	temp = output[(output.index('=') + 1):output.rindex("'")]
	return float(temp)

# ------------------------------

#
# MQTT Setup
#

MQTT_SERVER = os.getenv('MQTT_SERVER')
MQTT_PORT = os.getenv('MQTT_PORT')
MQTT_LOGIN = os.getenv('MQTT_LOGIN')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_TOPIC_PREFIX = "BeeHiveMonitor/1/"
MQTT_TOPIC_PREFIX_CMD = MQTT_TOPIC_PREFIX + "cmd/"
MQTT_TOPIC_PREFIX_STATE = MQTT_TOPIC_PREFIX + "state/"

I2C_BUS = int(os.getenv('I2C_BUS'))

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

#
# BME180 setup
#
import Adafruit_BMP.BMP085 as BMP085

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

# Initialise the BME180
bme180 = BMP085.BMP085(busnum=I2C_BUS)

# Initialise the BME280
bus = SMBus(I2C_BUS)
bme280 = BME280(i2c_dev=bus, i2c_addr=0x77)

factor = 1.2  # Smaller numbers adjust temp down, vice versa
smooth_size = 10  # Dampens jitter due to rapid CPU temp changes
cpu_temps = []

#
# ADPS-9960 setup
#
from apds9960.const import *
from apds9960 import APDS9960

dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
}

try:
	# Initialise the ADPS-9960
	apds = APDS9960(bus)
	apds.enableLightSensor()
	#apds.enableGestureSensor()
	apds.enableProximitySensor()
except:
	print("No ADPS-9960 detected")

while True:
	# Connect / Reconnect up MQTT
	if not mqtt_connected:
		print("Connecting to broker")

		client.connect(MQTT_SERVER, int(MQTT_PORT), 60)

		# TODO: Check failure here
		while not mqtt_connected:
			client.loop()

		# Setup some retained values for units
		client.publish(MQTT_TOPIC_PREFIX_STATE + "temperature/units", "°C", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "compensated_temperature/units", "°C", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "pressure/units", "hPa", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "sealevel_pressure/units", "hPa", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "relative_humidity/units", "%", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "altitude/units", "m", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "ambient_light/units", "byte", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "red/units", "byte", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "green/units", "byte", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "blue/units", "byte", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "proximity/units", "byte", retain=True);

	# Read in values from BME180
	try:
		raw_temp = bme180.read_temperature()
		pressure = bme180.read_pressure()
		altitude = bme180.read_altitude()
		sealevel_pressure = bme180.read_sealevel_pressure()

		client.publish(MQTT_TOPIC_PREFIX_STATE + "temperature", raw_temp)
		# Compensated temperature is not right, possibly because CPU temp is quite different
		#client.publish(MQTT_TOPIC_PREFIX_STATE + "compensated_temperature", comp_temp);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "pressure", pressure)
		client.publish(MQTT_TOPIC_PREFIX_STATE + "altitude", altitude)
		client.publish(MQTT_TOPIC_PREFIX_STATE + "sealevel_pressure", sealevel_pressure)
	except:
		pass

	# Read in values from BME280 (todo: Look at if we can improve accuracy/use IIR
	try:
		cpu_temp = get_cpu_temperature()
		cpu_temps.append(cpu_temp)

		if len(cpu_temps) > smooth_size:
	        	cpu_temps = cpu_temps[1:]

		smoothed_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
		raw_temp = bme280.get_temperature()
		comp_temp = raw_temp - ((smoothed_cpu_temp - raw_temp) / factor)

		pressure = bme280.get_pressure()
		humidity = bme280.get_humidity()
		print('Temp: {:05.2f}*C Compensated Temp: {:05.2f}*C Pressure: {:05.2f}hPa Relative Humidity: {:05.2f}%'.format(raw_temp, comp_temp, pressure, humidity))

		# TODO: Work out how to calculate relative altitude. QNH ? METAR ?

		client.publish(MQTT_TOPIC_PREFIX_STATE + "temperature", raw_temp);
		# Compensated temperature is not right, possibly because CPU temp is quite different
		client.publish(MQTT_TOPIC_PREFIX_STATE + "compensated_temperature", comp_temp);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "pressure", pressure);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "relative_humidity", humidity);
	except:
		pass

	# Read in values from ADPS-9960
	try:
		ambient_light = apds.readAmbientLight()
		r = apds.readRedLight()
		g = apds.readGreenLight()
		b = apds.readBlueLight()
		print("AmbientLight={} (R: {}, G: {}, B: {})".format(ambient_light, r, g, b))

		client.publish(MQTT_TOPIC_PREFIX_STATE + "ambient_light", ambient_light);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "red", r);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "green", g);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "blue", b);

		# Measure proximity
		proximity = apds.readProximity()
		print("Proximity={}".format(proximity))
		client.publish(MQTT_TOPIC_PREFIX_STATE + "proximity", proximity);

		# Not entirely sure what use this is in the context of bees but why not!
		# -disabled as I think it might be blocking reads
#		if apds.isGestureAvailable():
#			motion = apds.readGesture()
#			gesture = dirs.get(motion, "unknown")
#			print("Gesture={}".format(gesture))
#			client.publish(MQTT_TOPIC_PREFIX_STATE + "gesture", gesture);
	except:
		pass

	# Process MQTT messages
	client.loop();

	# Wait a bit
	time.sleep(5)
