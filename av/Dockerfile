
FROM dynamicdevices/bee-monitor-base-image

RUN apk add python3 python3-dev py3-pip py3-wheel raspberrypi alpine-sdk minicom
RUN export READTHEDOCS=True && pip3 install picamera
RUN pip install paho-mqtt rpi.gpio ffmpeg-python

# Enable OpenRC
ENV INITSYSTEM on 

COPY scripts .
COPY *.ttf .

CMD ./autorun.sh 


