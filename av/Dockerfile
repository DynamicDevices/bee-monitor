
FROM dynamicdevices/bee-monitor-base-image

RUN apk add python3 python3-dev py3-pip py3-wheel raspberrypi alpine-sdk
RUN export READTHEDOCS=True && pip3 install picamera
RUN pip install rpi.gpio

# Enable OpenRC
ENV INITSYSTEM on 

COPY scripts .

CMD ./autorun.sh 


