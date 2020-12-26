#!/usr/bin/env python3
## This Python script sends picamera video output to stout,
## it is intended to be called from a bash script which pipes

## the output into ffmpeg

## Bash script is startPythonStream.sh

import os
import time
import picamera
import sys
from signal import pause
from datetime import datetime

sys.stdout = os.fdopen(sys.stdout.fileno(), 'wb', 0)

#---------------------------------------------------------

## Start capturing video

with picamera.PiCamera() as camera:
  camera.resolution = (1280, 720)
  camera.framerate = 25
  camera.vflip = False
  camera.hflip = False
#  camera.annotate_background = picamera.Color('black')
#  camera.annotate_foreground = picamera.Color('yellow')
#  camera.annotate_text_size = 24
  camera.start_recording(sys.stdout, bitrate = 2500000, format='h264')
#  camera.start_recording(sys.stdout, bitrate = 2500000, format='rgb')
  while True:
#      i = datetime.now()
#      now = i.strftime('%d %b %Y - %H:%M:%S')
#      camera.annotate_text = ' BeeCam - ' + now + ' ' + 'Temp = ?'
#      camera.wait_recording(0.2)
      time.sleep(1)

