
#!/bin/sh

# FFMPEG

WIDTH=640
HEIGHT=480
FPS=25
BITRATE=1M
POS_X=4
POS_Y=4
FONTFILE=Verdana.ttf

#
# Overlay from file
#

#
# Overlay string
#

ffmpeg -nostats -f lavfi -i aevalsrc=0 -f v4l2 -framerate ${FPS} -video_size ${WIDTH}x${HEIGHT} \
       -i /dev/video0 \
       -vf "drawtext=text='Tapestry BeeCamEndo %{gmtime}': fontfile=${FONTFILE}: x=${POS_X}: y=${POS_Y}: fontsize=24:fontcolor=yellow@0.6: box=1: boxcolor=black@0.4" \
       -codec:v h264_omx -b:v ${BITRATE} \
       -codec:a aac -map 0 -map 1:v \
       -f flv rtmp://a.rtmp.youtube.com/live2/${STREAM_KEY_ENDO}

#  sleep 10
