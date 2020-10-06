
FROM dynamicdevices/bee-monitor-base-image

# Enable OpenRC
ENV INITSYSTEM on 

RUN apk add i2c-tools python3 py3-pip

RUN pip install paho-mqtt bmp280

COPY scripts/bmp280.py bmp280.py
COPY scripts/sleep.sh sleep.sh

CMD ./sleep.sh


