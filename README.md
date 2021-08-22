
# Bee Hive Monitor

Project to monitor hives with B4Biodiversity, initially based at DoES Liverpool.

![Bee Pic](https://github.com/DynamicDevices/bee-monitor/blob/master/beepic.jpg)

You can see (and hear!)  the initial Live Stream on [YouTube](https://www.youtube.com/watch?v=5LyV6GvAm94)
 
The architecture is as follows:

- Raspberry Pi 4 4GB with Power over Ethernet hat providing power to the system.
- Range of I2C sensors providing environmental information
- IR Raspberry Pi cam providing visual information about internals of hive
- USB microphone providing audio information about bee activity

The software is based upon the Balena Docker framework which gives us containerisation and remote access to the Raspberry Pi for updates and configuration

The hardware and sensors we've used are all documented [here](https://docs.google.com/spreadsheets/d/1hY-etsIJNC_ZLlRN6wujNqhEhVUt7ppHE7utuugSbvE/edit?usp=sharing)

We have two containers configured at this time both are based on an Alpine Linux image which is built seperately with dependencies needed (e.g. accelerated FFMPEG).

# Base container image

The image we use is called makespacelive-base-image and can be found [here](https://github.com/DynamicDevices/makespacelive-base-image)

This is built and pushed up to Docker Hub. The build artifact can be found [here](https://hub.docker.com/repository/docker/dynamicdevices/bee-monitor-base-image)

# AV container

This container supports streaming of a combined video and audio image from the Raspberry Pi IR camera and the USB camera.

It pipes the image data from the RPi camera, combines it with the audio and pushes it up to Youtube.

You need some configuration environment variables setup for this to work

These are needed for the GPU to handle the Raspberry Pi camera. I put them in the Balena Fleet Configuration

| Variable                        | Description                    |
| ------------------------------- | ------------------------------ |
| RESIN_HOST_CONFIG_gpu_mem_1024  | Set GPU memory on 1024MB board |
| RESIN_HOST_CONFIG_gpu_mem_512   | Set GPU memory on 512MB board  | 
| RESIN_HOST_CONFIG_gpu_mem_256   | Set GPU memory on 256MB board  |
| RESIN_HOST_CONFIG_start_x       | Support camera module          |

NB. If you aren't using Balena you can set these yourself into the Raspberry Pi `config.txt` file in the boot partition

Next you need some service environment variables which configure the streaming. Again I configure these within the Balena fleet configuration

| Variable                        | Description                    |
| ------------------------------- | ------------------------------ |
| AUTORUN                         | Automatically start streaming  |
| STREAM_KEY                      | Your own YouTube stream key    |

NB. You may not want streaming to start automatically. If you omit `AUTORUN` you can start streaming manually with `./stream.sh`

# Sensor Container

We are adding I2C sensors as we go. Sensor data is published to a cloud broker via MQTT

There are a number of service environment variables to configure sensing

| Variable                        | Description                      |
| ------------------------------- | -------------------------------- |
| AUTORUN                         | Automatically start sensing      |
| I2C_BUS                         | Bus for sensors (1 or 3 usually) |
| MQTT_LOGIN                      | MQTT login for broker            |
| MQTT_PASSWORD                   | MQTT password for broker         |
| MQTT_PORT                       | MQTT TCP port for broker (1883)  |
| MQTT_SERVER                     | MQTT server DNS/IP               |

NB. Currently we don't support MQTT over TLS

Sensor data is published on a topic `BeeHiveMonitor/${ID}/state/${sensor}`. There is a corresponding retained topic giving sense data point units `BeeHiveMonitor/${ID}/state/${sensor}/units`

e.g.

```
BeeHiveMonitor/1/state/temperature 24.16606980834024
BeeHiveMonitor/1/state/compensated_temperature 4.921127981957113
BeeHiveMonitor/1/state/pressure 1018.962260292171
BeeHiveMonitor/1/state/relative_humidity 37.66460667390904
BeeHiveMonitor/1/state/ambient_light 427
BeeHiveMonitor/1/state/red 89
BeeHiveMonitor/1/state/green 138
BeeHiveMonitor/1/state/blue 149
BeeHiveMonitor/1/state/proximity 13
```

## Viewing the telemetry data

With current settings you can subscribe to the data with the following command

```
mosquitto_sub -v -h mqtt.dynamicdevices.co.uk -t "BeeHiveMonitor/#"
```

## Supported Sensors

Currently supported sensors are as follows:

`i2cdetect ${bus}`

```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- 33 -- -- -- -- -- 39 -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- 4a -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- 77     
```

NB. All these sensors are 3V3 as we can't connect 5V sensors directly to the Raspberry Pi GPIO

| Sensor ID | Sensor Name                                                                             | Info |
| --------- | --------------------------------------------------------------------------------------- | ---- |
| 0x39,0x77 | WINGONEER® Temperature, Barometric, Altitude, Light, Humidity Five in One Sensor Module | Not installed - BME180 instead and publishing currently |
| 0x76      | BME280 temperature, humidity and pressure                                               | Pubishing data  |
| 0x68      | MakerHawk MPU-9250 9DOF Module 9 Axis Gyroscope Accelerometer Magnetic Field Sensor     | Publishing data |
| 0x4A      | GY-49-MAX44009 Digital Optical Intensity Flow Sensor                                    | Publishing data |
| 0x33      | Sparkfun MLX90640 IR array                                                              | Publishing data |

## EnviroPlus

There's an independent sensor unit comprising a Raspberry Pi Zero and an EnviroPlus sensor module chained onto the Raspberry Pi 4.

For details on the Enviroplus see [here](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-enviro-plus)

We use the code in the Enviroplus repository which is [here](https://github.com/pimoroni/enviroplus-python)

The code is built into a Balena docker container which is [here](https://github.com/DynamicDevices/enviroplus-docker-image)

The PiZero is configured as a USB RNDIS ethernet gadget so enumerates to the Pi4 in this way.

For details on how to configure the PiZero see the conversation [here](https://forums.balena.io/t/connecting-a-balena-rpi-zero-through-a-balena-rpi4/223479/6)

To configure up the RPi4 make the following changes to the host BalenaOS

```
mount -o remount,rw /
cd /lib/udev/rules.d
vi 85-nm-unmanaged.rules
```

Change the unmanaged status to 0

```
# USB gadget device. Unmanage by default, since whatever created it      
# might want to set it up itself (e.g. activate an ipv4.method=shared  
# connection).                                                  
ENV{DEVTYPE}=="gadget", ENV{NM_UNMANAGED}="0"  
```

This allows Network Manager to manage the usb device

Then prevent the usb gadget from being renamed

```
vi 80-net-setup-link.rules 
```

Comment out the following lines

```
#IMPORT{builtin}="net_setup_link"

#NAME=="", ENV{ID_NET_NAME}!="", NAME="$env{ID_NET_NAME}"
```

Lastly create a new file to share the network connection to the ethernet gadget

```
cd /mnt/boot/system-connections
vi usb
```

```
[connection]
id=usb
interface-name=usb0
type=ethernet

[ipv4]
method=shared

[ipv6]
method=ignore
```

Then synchronise the filesystem and reboot

```
sync
reboot
```

## Enable serial console

The AV docker container is configured to load the g_cdc module on startup. This module combines an ethernet device and a serial device to enable access to/from the Pi0

We implement this way as I have found that when adding the module to /etc/modules.d the Pi0 seems to fail to enumerate correctly on power up.

The serial device enumerates as /dev/ttyACM0 on the host PC. It is /dev/ttyGS0 on the Pi0.

To enable a serial console on the Pi0

```
mount -o remount,rw /
cd /etc/systemd/system/getty.target.wants
systemctl enable serial-getty\@ttyGS0.service 
mount -o remount,ro /
reboot
```

You can then use minicom or a similar terminal emulator to access the shell on the Pi0. 

This can be useful if you have trouble with, say, ethernet connectivity
