ffmpeg -f lavfi -i "sine=frequency=1000:duration=5" -c:a pcm_s16le sing_test.wav
