
FROM dynamicdevices/bee-monitor-base-image

# Enable OpenRC
ENV INITSYSTEM on 

RUN apk add i2c-utils

COPY scripts/bmp280.sh bmp280.sh
COPY scripts/sleep.sh sleep.sh

CMD ./sleep.sh


