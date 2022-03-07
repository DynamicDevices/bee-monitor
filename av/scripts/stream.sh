#!/bin/sh

amixer -c 1 set "Mic" 75%

# Make sure there is a default file for the overlay text
if [ ! -f "/data/info.txt" ]; then
    cp info.txt /data
fi

# FFMPEG

POS_X=4
POS_Y=4
FONTFILE=Verdana.ttf

if [ -z ${WIDTH+x} ]; then
WIDTH=1280
fi
if [ -z ${HEIGHT+x} ]; then
HEIGHT=720
fi
if [ -z ${BITRATE+x} ]; then
BITRATE=2500000
fi
if [ -z ${FPS+x} ]; then
FPS=25
fi
if [ -z ${VOLUME_GAIN+x} ]; then
VOLUME_GAIN=20dB
fi

#
# Overlay from file
#

#/opt/vc/bin/raspivid -o - -t 0 -w ${WIDTH} -h ${HEIGHT} -fps ${FPS} -b ${BITRATE} | \
#    ffmpeg -f alsa -thread_queue_size 1024 -ac 1 -i hw:1 -f h264 -i - \
#    -vf "drawtext=textfile=/data/info.txt: fontfile=${FONTFILE}: reload=1: x=${POS_X}: y=${POS_Y}: fontsize=24:fontcolor=yellow@0.6: box=1: boxcolor=black@0.4" \
#    -codec:v h264_omx -b:v ${BITRATE} -c:a aac -ar 44100 -b:a 128k -f flv rtmp://a.rtmp.youtube.com/live2/${STREAM_KEY}

#
# Overlay string
#

# This fails after some hours...

#/opt/vc/bin/raspivid -o - -t 0 -w ${WIDTH} -h ${HEIGHT} -fps ${FPS} -b ${BITRATE} | \
#    ffmpeg \
#    -f alsa -thread_queue_size 1024 -ac 1 -i hw:1 \
#    -f h264 -i - \
#    -vf "drawtext=text='Tapestry BeeCam %{gmtime}': fontfile=${FONTFILE}: x=${POS_X}: y=${POS_Y}: fontsize=24:fontcolor=yellow@0.6: box=1: boxcolor=black@0.4" \
#    -codec:v h264_omx -b:v ${BITRATE} \
#    -filter:a "volume=${VOLUME_GAIN}" \
#    -c:a aac -ar 44100 -b:a 128k \
#    -f flv rtmp://${STREAM_URL}/${STREAM_KEY} \
#    | tee /data/ffmpeg.log

# Simplify for testing

#/opt/vc/bin/raspivid -o - -t 0 -w ${WIDTH} -h ${HEIGHT} -fps ${FPS} -b ${BITRATE} | \
#    ffmpeg \
#    -f alsa \
#    -thread_queue_size 1024 \
#    -ac 1 -i hw:1 \
#    -thread_queue_size 1024 \
#    -f h264 -i - \
#    -codec:v h264_omx -b:v ${BITRATE} \
#    -filter:a "volume=${VOLUME_GAIN}" \
#    -c:a aac -ar 44100 -b:a 128k \
#    -f flv rtmp://${STREAM_URL}/${STREAM_KEY} \
#    | tee /data/ffmpeg.log

/opt/vc/bin/raspivid -o - -t 0 -vf -w ${WIDTH} -h ${HEIGHT} -fps ${FPS} -b ${BITRATE} | \
    ffmpeg \
    -use_wallclock_as_timestamps 1 \
    -f alsa \
    -thread_queue_size 1024 \
    -ac 1 -i hw:1 \
    -f h264 \
    -thread_queue_size 1024 \
    -i - \
    -fflags +genpts \
    -codec:v copy \
    -filter:a "volume=${VOLUME_GAIN}" \
    -codec:a aac -ar 44100 -b:a 128k \
    -f flv rtmp://${STREAM_URL}/${STREAM_KEY} \
    | tee /data/ffmpeg.log
