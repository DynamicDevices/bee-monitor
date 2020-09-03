FROM balenalib/raspberrypi3-alpine:latest

# Enable OpenRC
ENV INITSYSTEM on 

RUN apk add ffmpeg alsa-utils raspberrypi

COPY scripts/sleep.sh sleep.sh

CMD ./sleep.sh 


