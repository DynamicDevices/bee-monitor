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

UNITS_SUFFIX = "/units"

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

# MPU9250 setup
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250

# Initialise the BME180
try:
    bme180 = BMP085.BMP085(busnum=I2C_BUS)
except:
    print("Error initialising BME180")

# Initialise the BME280
try:
    bus = SMBus(I2C_BUS)
    bme280 = BME280(i2c_dev=bus, i2c_addr=0x77)
except:
    print("Error initialising BME280")

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

#
# MPU9250 setup
#
try:
	mpu = MPU9250(
	address_ak=AK8963_ADDRESS,
	address_mpu_master=MPU9050_ADDRESS_68, # In 0x68 Address
	address_mpu_slave=None,
	bus=1,
	gfs=GFS_1000,
	afs=AFS_8G,
	mfs=AK8963_BIT_16,
	mode=AK8963_MODE_C100HZ)

	mpu.configure() # Apply the settings to the registers.
except:
	print("No MPU9250 detected")

#
# MAX44009 setup
#
import max44009

try:
	max_sensor = max44009.MAX44009(1, 0x4a)
	max_sensor.configure(cont=0, manual=0, cdr=0, timer=0)
except:
	print("No MAX44009 detected")

#
# MLX90640 setup
#
import seeed_mlx90640

try:
	mlx = seeed_mlx90640.grove_mxl90640()
	mlx.refresh_rate = seeed_mlx90640.RefreshRate.REFRESH_0_5_HZ  # Could speed this up ?
	frame = [0] * 768
except:
	print("No MX90640 detected")

#
# Main loop
#
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

		# Setup some retained values for units
		client.publish(MQTT_TOPIC_PREFIX_STATE + "temperature_cpu" + UNITS_SUFFIX, "°C", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "temperature_bme180" + UNITS_SUFFIX, "°C", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "temperature_bme280" + UNITS_SUFFIX, "°C", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "compensated_temperature_bme280" + UNITS_SUFFIX, "°C", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "pressure" + UNITS_SUFFIX, "hPa", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "sealevel_pressure" + UNITS_SUFFIX, "hPa", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "relative_humidity" + UNITS_SUFFIX, "%", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "altitude" + UNITS_SUFFIX, "m", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "ambient_light" + UNITS_SUFFIX, "byte", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "red" + UNITS_SUFFIX, "byte", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "green" + UNITS_SUFFIX, "byte", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "blue" + UNITS_SUFFIX, "byte", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "proximity" + UNITS_SUFFIX, "byte", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "accelerometer_x" + UNITS_SUFFIX, "g", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "accelerometer_y" + UNITS_SUFFIX, "g", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "accelerometer_z" + UNITS_SUFFIX, "g", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "gyroscope_x" + UNITS_SUFFIX, "°/s", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "gyroscope_y" + UNITS_SUFFIX, "°/s", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "gyroscope_z" + UNITS_SUFFIX, "°/s", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "magnetometer_x" + UNITS_SUFFIX, "µT", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "magnetometer_y" + UNITS_SUFFIX, "µT", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "magnetometer_z" + UNITS_SUFFIX, "µT", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "temperature_mpu9250" + UNITS_SUFFIX, "°C", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "luminance" + UNITS_SUFFIX, "lux", retain=True);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "ir_frame" + UNITS_SUFFIX, "byte[]", retain=True);

	# Read in values from BME180
	try:
		raw_temp = bme180.read_temperature()
		pressure = bme180.read_pressure()
		altitude = bme180.read_altitude()
		sealevel_pressure = bme180.read_sealevel_pressure()

		client.publish(MQTT_TOPIC_PREFIX_STATE + "temperature_bme180", raw_temp)
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

		client.publish(MQTT_TOPIC_PREFIX_STATE + "temperature_bme280", raw_temp);
		# Compensated temperature is not right, possibly because CPU temp is quite different
		client.publish(MQTT_TOPIC_PREFIX_STATE + "compensated_temperature_bme280", comp_temp);
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

	# Read in values from MPU9250
	try:
		acc_x,acc_y,acc_z = mpu.readAccelerometerMaster()
		gyro_x,gyro_y,gyro_z = mpu.readGyroscopeMaster()
		magneto_x,magneto_y,magneto_z = mpu.readMagnetometerMaster()
		temp = mpu.readTemperatureMaster()

		client.publish(MQTT_TOPIC_PREFIX_STATE + "accelerometer_x", acc_x);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "accelerometer_y", acc_y);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "accelerometer_z", acc_z);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "gyroscope_x", gyro_x);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "gyroscope_y", gyro_y);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "gyroscope_z", gyro_z);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "magnetometer_x", magneto_x);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "magnetometer_y", magneto_y);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "magnetometer_z", magneto_z);
		client.publish(MQTT_TOPIC_PREFIX_STATE + "temperature_mpu9250", temp);

	except:
		pass

	# Read in values from MAX44009
	try:
		luminance =  max_sensor.luminosity()

		client.publish(MQTT_TOPIC_PREFIX_STATE + "luminance", luminance);
	except:
		pass

	# Read in values from MLX90640
	try:
		mlx.getFrame(frame)
		client.publish(MQTT_TOPIC_PREFIX_STATE + "ir_frame", str(frame));
	except:
		pass

	# Now write to file
	f = open("/data/info.txt.new", "w")
	f.write("Tapestry BeeCam %{gmtime}\r\n" + "Temp: {} °C\r\nPressure: {} hPa\r\nLuminance: {} lux".format(raw_temp, pressure, luminance))
	f.flush()
	os.fsync(f.fileno())
	f.close()
	os.rename("/data/info.txt.new", "/data/info.txt")

	# Process MQTT messages
	client.loop();

	# Wait a bit
	time.sleep(5)
