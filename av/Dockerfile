FROM dynamicdevices/bee-monitor-base-image

# Enable OpenRC
ENV INITSYSTEM on 

COPY scripts/sleep.sh sleep.sh
COPY scripts/stream.sh stream.sh

CMD ./sleep.sh 


