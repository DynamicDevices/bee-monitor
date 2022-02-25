
FROM balenalib/raspberrypi-4-64-golang

# Enable OpenRC
ENV INITSYSTEM on 

GO111MODULE=on go install github.com/prometheus/prometheus/cmd/...

CMD prometheus --config.file=your_config.yml
