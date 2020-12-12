
FROM dynamicdevices/bee-monitor-base-image

# Enable OpenRC
ENV INITSYSTEM on 

RUN apk --no-cache add i2c-tools python3 py3-pip git gcc python3-dev musl-dev linux-headers

RUN pip install paho-mqtt pimoroni-bme280 smbus2 apds9960 mpu9250-jmdev

RUN git clone https://github.com/adafruit/Adafruit_Python_BMP.git && cd Adafruit_Python_BMP && python3 setup.py install

COPY scripts/ .

CMD ./autorun.sh
