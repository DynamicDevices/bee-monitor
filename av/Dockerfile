
FROM dynamicdevices/bee-monitor-base-image

RUN pip2 install picamera

# Enable OpenRC
ENV INITSYSTEM on 

COPY scripts .

CMD ./autorun.sh 


