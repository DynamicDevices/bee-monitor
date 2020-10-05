
FROM dynamicdevices/bee-monitor-base-image

# Enable OpenRC
ENV INITSYSTEM on 

COPY scripts/bmp280.sh bmp280.sh
COPY scripts/sleep.sh sleep.sh

CMD ./sleep.sh


