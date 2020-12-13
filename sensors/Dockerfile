
FROM dynamicdevices/bee-monitor-base-image

# Enable OpenRC
ENV INITSYSTEM on 

RUN apk --no-cache add i2c-tools python3 py3-pip git gcc python3-dev musl-dev linux-headers py3-wheel make

RUN pip install paho-mqtt pimoroni-bme280 smbus smbus2 apds9960 mpu9250-jmdev rpi.gpio seeed-python-mlx90640

RUN git clone https://github.com/adafruit/Adafruit_Python_BMP.git && cd Adafruit_Python_BMP && python3 setup.py install

RUN git clone https://github.com/josecastroleon/max44009.git && cp max44009/max44009.py .

RUN git clone https://github.com/Seeed-Studio/grove.py && cd grove.py && pip install .

COPY scripts/ .

CMD ./autorun.sh
