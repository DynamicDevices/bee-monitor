
#!/bin/sh

while [ True ];
do

# FFMPEG

#  /opt/vc/bin/raspivid -o - -t 0 -vf -hf -fps 30 -b 6000000 | ffmpeg -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv rtmp://a.rtmp.youtube.com/live2/${STREAM_KEY}
/opt/vc/bin/raspivid -o - -t 0 -w 1280 -h 720 -vf -fps 25 -b 6000000 | ffmpeg -f alsa -thread_queue_size 1024 -ac 1 -i hw:1 -f h264 -i - -vcodec copy -c:a aac -ar 44100 -b:a 128k -f flv rtmp://a.rtmp.youtube.com/live2/${STREAM_KEY}
  sleep 10

# GStreamer1.0

export LD_LIBRARY_PATH=/opt/vc/lib
export GST_PLUGIN_PATH=/usr/lib/gstreamer-1.0

done

