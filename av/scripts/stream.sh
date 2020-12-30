
#!/bin/sh

amixer -c 1 set "Mic" 100%

# Make sure there is a default file for the overlay text
if [ ! -f "/data/info.txt" ]; then
    cp info.txt /data
fi

# FFMPEG

WIDTH=1280
HEIGHT=720
FPS=25
BITRATE=2500000
POS_X=4
POS_Y=4
FONTFILE=Verdana.ttf
VOLUME_GAIN=20dB

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

/opt/vc/bin/raspivid -o - -t 0 -w ${WIDTH} -h ${HEIGHT} -fps ${FPS} -b ${BITRATE} | \
    ffmpeg -nostats \
    -f alsa -thread_queue_size 1024 -ac 1 -i hw:1 \
    -f h264 -i - \
    -vf "drawtext=text='Tapestry BeeCam %{gmtime}': fontfile=${FONTFILE}: x=${POS_X}: y=${POS_Y}: fontsize=24:fontcolor=yellow@0.6: box=1: boxcolor=black@0.4" \
    -codec:v h264_omx -b:v ${BITRATE} \
    -filter:a "volume=${VOLUME_GAIN}" \
    -c:a aac -ar 44100 -b:a 128k \
    -f flv rtmp://${STREAM_URL}/${STREAM_KEY}

#  sleep 10
