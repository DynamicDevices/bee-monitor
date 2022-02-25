
FROM balenalib/raspberrypi4-64-golang

RUN GO111MODULE=on go install github.com/prometheus/prometheus/cmd/...

CMD prometheus --config.file=your_config.yml
