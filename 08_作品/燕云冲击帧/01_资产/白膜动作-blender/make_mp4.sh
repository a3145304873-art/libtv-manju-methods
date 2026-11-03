#!/usr/bin/env bash
# 把 frames/<片名>/f0001..f0096.png 合成 24fps H.264 MP4
set -e
cd "$(dirname "$0")/frames"
for d in */; do
  name="${d%/}"
  ffmpeg -y -framerate 24 -i "$name/f%04d.png" -c:v libx264 -crf 18 -pix_fmt yuv420p "../${name}.mp4" -loglevel error
  echo "MP4-OK ${name}"
done
