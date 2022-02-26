
FROM balenalib/raspberrypi4-64-golang

RUN install_packages npm

RUN mkdir -p $GOPATH/src/github.com/node_exporter
RUN cd $GOPATH/src/github.com/node_exporter
RUN git clone https://github.com/prometheus/node_exporter.git
RUN cd node_exporter && ( make || : )

CMD cd node_exporter && ./node_exporter
