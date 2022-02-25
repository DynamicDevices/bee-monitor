
FROM balenalib/raspberrypi4-64-golang

RUN mkdir -p $GOPATH/src/github.com/prometheus
RUN cd $GOPATH/src/github.com/prometheus
RUN git clone https://github.com/prometheus/prometheus.git
RUN cd prometheus
RUN make build

CMD ./prometheus --config.file=your_config.yml
