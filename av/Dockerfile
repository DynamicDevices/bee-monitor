FROM resin/raspberrypi3-debian:stretch

##
## Setup & Install Dependencies
##

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

# Install dependencies
RUN apt-get update \
    && apt-get install -y dnsmasq wireless-tools dbus xterm \
                          v4l-utils nano bc wget unzip netcat alsa-utils build-essential git usbutils openssh-server \
                          python3 python3-gi python3-pip python3-setuptools python3-matplotlib\
                          autoconf automake libtool pkg-config \
                          libraspberrypi-dev \
                          libmp3lame-dev libx264-dev yasm git libass-dev libfreetype6-dev libtheora-dev libvorbis-dev \
                          texi2html zlib1g-dev libomxil-bellagio-dev libasound2-dev \
                          cmake \
                          ocl-icd-opencl-dev \
                          libjpeg-dev libtiff5-dev libjasper-dev libpng-dev \
                          libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
                          libgtk2.0-dev libatlas-base-dev gfortran \
			  apt-transport-https \
                          default-jre \
                          build-essential autotools-dev automake autoconf \
                          libtool autopoint libxml2-dev zlib1g-dev libglib2.0-dev \
                          pkg-config bison flex python3 git gtk-doc-tools libasound2-dev \
                          libgudev-1.0-dev libxt-dev libvorbis-dev libcdparanoia-dev \
                          libpango1.0-dev libtheora-dev libvisual-0.4-dev iso-codes \
                          libgtk-3-dev libraw1394-dev libiec61883-dev libavc1394-dev \
                          libv4l-dev libcairo2-dev libcaca-dev libspeex-dev libpng-dev \
                          libshout3-dev libjpeg-dev libaa1-dev libflac-dev libdv4-dev \
                          libtag1-dev libwavpack-dev libpulse-dev libsoup2.4-dev libbz2-dev \
                          libcdaudio-dev libdc1394-22-dev ladspa-sdk libass-dev \
                          libcurl4-gnutls-dev libdca-dev libdirac-dev libdvdnav-dev \
                          libexempi-dev libexif-dev libfaad-dev libgme-dev libgsm1-dev \
                          libiptcdata0-dev libkate-dev libmimic-dev libmms-dev \
                          libmodplug-dev libmpcdec-dev libofa0-dev libopus-dev \
                          librsvg2-dev librtmp-dev libschroedinger-dev libslv2-dev \
                          libsndfile1-dev libsoundtouch-dev libspandsp-dev libx11-dev \
                          libxvidcore-dev libzbar-dev libzvbi-dev liba52-0.7.4-dev \
                          libcdio-dev libdvdread-dev libmad0-dev libmp3lame-dev \
                          libmpeg2-4-dev libopencore-amrnb-dev libopencore-amrwb-dev \
                          libsidplay1-dev libtwolame-dev libx264-dev libusb-1.0 \
                          yasm python-gi-dev python3-dev libgirepository1.0-dev \
                          gettext \
                          libjson-glib-dev libopus-dev libvpx-dev \
                          libssl-dev libvo-aacenc-dev

# Kludge to get libfaac-dev for aac enc (actually might not need this...)
RUN echo "deb http://www.deb-multimedia.org/ wheezy main non-free sudo" >> /etc/apt/sources.list
RUN apt-get update && apt-get install deb-multimedia-keyring --allow-unauthenticated && apt-get update && apt-get install -y libfaac-dev

# Trouble building these so use packaged versions...
#RUN git clone https://salsa.debian.org/pkg-voip-team/libsrtp2.git
#RUN cd libsrtp2 && ./configure && make install
#RUN cd / && find -name libsrtp*
RUN wget http://ftp.uk.debian.org/debian/pool/main/libp/libpcap/libpcap0.8_1.8.1-6_armhf.deb
RUN dpkg -i libpcap0.8_1.8.1-6_armhf.deb
RUN wget http://ftp.uk.debian.org/debian/pool/main/libp/libpcap/libpcap0.8-dev_1.8.1-6_armhf.deb
RUN dpkg -i libpcap0.8-dev_1.8.1-6_armhf.deb
RUN wget http://ftp.uk.debian.org/debian/pool/main/libs/libsrtp2/libsrtp2-1_2.2.0-1_armhf.deb
RUN dpkg -i libsrtp2-1_2.2.0-1_armhf.deb
RUN wget http://ftp.uk.debian.org/debian/pool/main/libs/libsrtp2/libsrtp2-dev_2.2.0-1_armhf.deb
RUN dpkg -i libsrtp2-dev_2.2.0-1_armhf.deb

##
## Start building
##

RUN pip3 install numpy

#
# Build OpenH264
#
RUN git clone https://github.com/cisco/openh264 && cd openh264 && make && make install

#
# Clone gstreamer git repos if they are not there yet
#
RUN [ ! -d gstreamer ] && git clone git://anongit.freedesktop.org/git/gstreamer/gstreamer && cd gstreamer && git show
RUN [ ! -d gst-plugins-base ] && git clone git://anongit.freedesktop.org/git/gstreamer/gst-plugins-base && cd gst-plugins-base && git show
RUN [ ! -d gst-plugins-good ] && git clone git://anongit.freedesktop.org/git/gstreamer/gst-plugins-good && cd gst-plugins-good && git show
RUN [ ! -d gst-plugins-bad ] && git clone git://anongit.freedesktop.org/git/gstreamer/gst-plugins-bad && cd gst-plugins-bad && git show
RUN [ ! -d gst-plugins-ugly ] && git clone git://anongit.freedesktop.org/git/gstreamer/gst-plugins-ugly && cd gst-plugins-ugly && git show
RUN [ ! -d gst-omx ] && git clone git://anongit.freedesktop.org/git/gstreamer/gst-omx && cd gst-omx && git show

#
# GStreamer
#
RUN export LD_LIBRARY_PATH=/usr/lib && cd gstreamer && ./autogen.sh --prefix=/usr --disable-gtk-doc --disable-examples && make -j4 && make install

# GStreamer plugins { base, good }
RUN cd gst-plugins-base &&  sed '14d' -i Makefile.am
RUN cd gst-plugins-base && ./autogen.sh --prefix=/usr --disable-gtk-doc --disable-examples && make -j4 && make install
RUN cd gst-plugins-good && ./autogen.sh --prefix=/usr --disable-gtk-doc --disable-examples && make -j4 && make install

#
# Build needed version of nice for Gstreamer plugins bad
#
RUN wget https://nice.freedesktop.org/releases/libnice-0.1.14.tar.gz
RUN tar xaf libnice-0.1.14.tar.gz && cd libnice-0.1.14 && ./configure --prefix=/usr --with-gstreamer && make -j4 install

#
# Build lksctp
#
RUN git clone git://github.com/sctp/lksctp-tools.git
RUN cd lksctp-tools && git checkout lksctp-tools-1.0.17
RUN cd lksctp-tools && ./bootstrap

#
# Build OpenCV (after we've built GStreamer so it gets detected
#
RUN cd ~ && git clone https://github.com/Itseez/opencv.git
RUN cd ~ && cd opencv && git checkout 3.4.3
RUN cd ~ && git clone https://github.com/opencv/opencv_contrib.git
RUN cd ~ && cd opencv_contrib && git checkout 3.4.3
RUN cd ~ && cd opencv && mkdir build && cd build && cmake -DOPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
            -DCMAKE_BUILD_TYPE=Release \
            -DCMAKE_INSTALL_PREFIX=/usr \
            -D ENABLE_NEON=ON \
            -D ENABLE_VFPV3=ON \
            -D BUILD_TESTS=OFF \
            -D INSTALL_PYTHON_EXAMPLES=OFF \
            -D BUILD_EXAMPLES=OFF .. \
         && make \
         && make install \
         && ldconfig

#
# Gstreamer-plugins-bad
#
RUN cd gst-plugins-bad && ./autogen.sh --prefix=/usr --disable-gtk-doc \
 && export CFLAGS='-I/opt/vc/include -I/opt/vc/include/interface/vcos/pthreads -I/opt/vc/include/interface/vmcs_host/linux/' \
 && export LDFLAGS='-L/opt/vc/lib' \
 && ./configure --prefix=/usr CFLAGS='-I/opt/vc/include -I/opt/vc/include/interface/vcos/pthreads -I/opt/vc/include/interface/vmcs_host/linux/' LDFLAGS='-I/opt/vc/lib' \
--disable-gtk-doc --disable-opengl --enable-gles2 --enable-egl --disable-glx \
--disable-x11 --disable-wayland --enable-dispmanx \
--with-gles2-module-name=/opt/vc/lib/libGLESv2.so \
--with-egl-module-name=/opt/vc/lib/libEGL.so \
--enable-webrtc --disable-examples
RUN cd gst-plugins-bad && make CFLAGS+='-Wno-error -Wno-redundant-decls' LDFLAGS+='-L/opt/vc/lib' -j4 && sudo make install

# GStreamer OMX support
RUN cd gst-omx && export LDFLAGS='-L/opt/vc/lib' \
CFLAGS='-I/opt/vc/include -I/opt/vc/include/IL -I/opt/vc/include/interface/vcos/pthreads -I/opt/vc/include/interface/vmcs_host/linux -I/opt/vc/include/IL' \
CPPFLAGS='-I/opt/vc/include -I/opt/vc/include/IL -I/opt/vc/include/interface/vcos/pthreads -I/opt/vc/include/interface/vmcs_host/linux -I/opt/vc/include/IL' \
&& ./autogen.sh --prefix=/usr --disable-gtk-doc --with-omx-target=rpi \
&& make CFLAGS+='-Wno-error -Wno-redundant-decls' LDFLAGS+='-L/opt/vc/lib' -j4 \
&& sudo make install

#
# GStreamer  gst-rpicamsrc
#
RUN git clone https://github.com/thaytan/gst-rpicamsrc.git
RUN cd gst-rpicamsrc && ./autogen.sh --prefix=/usr && make && make install

#
# Install FFMPEG Python bindings
#
#RUN pip3 install wheel
#RUN pip3 install ffmpeg-python

#
# Build FFMPEG
#
#RUN cd ~ \
#    && git clone git://source.ffmpeg.org/ffmpeg.git ffmpeg 
#RUN cd ~/ffmpeg \
#    && ./configure --enable-libfreetype --enable-gpl --enable-nonfree --enable-libx264 --enable-libass \
#                  --enable-libmp3lame --prefix=/usr --enable-omx --enable-omx-rpi --enable-indev=alsa --enable-outdev=alsa
#RUN cd ~/ffmpeg \
#    && make
#RUN cd ~/ffmpeg \
#    && make install

#
# Install Jupyter
#
#RUN python3 -m pip install jupyter


