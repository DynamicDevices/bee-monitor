#!/bin/env python3

# Convert images to avi
#     ffmpeg -f image2 -r 2 -i mlx90640_test_fliplr_%d.png -r 25 video.avi
# Convert avi to gif
#     ffmpeg -i video.avi -pix_fmt rgb24 -loop_output 0 out.gif

##########################################
# MLX90640 Thermal Camera w Raspberry Pi
# -- 2Hz Sampling with Simple Routine
##########################################
#
#import time,board,busio
import time
import numpy as np
#import adafruit_mlx90640
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt

#i2c = busio.I2C(board.SCL, board.SDA, frequency=400000) # setup I2C
#mlx = adafruit_mlx90640.MLX90640(i2c) # begin MLX90640 with I2C comm
#mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_8_HZ # set refresh rate
mlx_shape = (24,32)

# setup the figure for plotting
plt.ion() # enables interactive plotting
fig,ax = plt.subplots(figsize=(12,7))
therm1 = ax.imshow(np.zeros(mlx_shape),vmin=0,vmax=60) #start plot with zeros
cbar = fig.colorbar(therm1) # setup colorbar for temps
cbar.set_label('Temperature [$^{\circ}$C]',fontsize=14) # colorbar label

frame = np.zeros((24*32,)) # setup array for storing all 768 temperatures
t_array = []

new_data = False

def on_message(client, userdata, message):
    global frame,new_data
    print("New IR data")
    frame = eval(message.payload.decode("utf-8"))
    new_data = True

client =mqtt.Client()
client.connect("mqtt.dynamicdevices.co.uk")
client.subscribe("BeeHiveMonitor/1/state/ir_frame")
client.on_message=on_message
client.loop_start()

idx=1

while True:

    t1 = time.monotonic()
    try:
#        mlx.getFrame(frame) # read MLX temperatures into frame var

        if new_data == True:
            data_array = (np.reshape(frame,mlx_shape)) # reshape to 24x32
            therm1.set_data(np.fliplr(data_array)) # flip left to right
            therm1.set_clim(vmin=np.min(data_array),vmax=np.max(data_array)) # set bounds
            cbar.on_mappable_changed(therm1) # update colorbar range
            plt.pause(0.001) # required
            fig.savefig('mlx90640_test_fliplr_' + str(idx) + '.png',dpi=300,facecolor='#FCFCFC',
                    bbox_inches='tight') # comment out to speed up
            t_array.append(time.monotonic()-t1)
            idx = idx + 1
            new_data = False

#        print('Sample Rate: {0:2.1f}fps'.format(len(t_array)/np.sum(t_array)))
    except ValueError:
        continue # if error, just read again

