
FROM dynamicdevices/bee-monitor-base-image

RUN apk add python3 py3-pip py3-wheel raspberrypi
RUN export READTHEDOCS=True && pip3 install picamera

# Enable OpenRC
ENV INITSYSTEM on 

COPY scripts .

CMD ./autorun.sh 


