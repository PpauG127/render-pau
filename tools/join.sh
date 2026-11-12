#!/bin/bash
# join.sh <parts_dir> <out_dir> <video...> : concat scene_XX.mp4 of each video without re-encoding
set -e; P=$1; O=$2; shift 2; mkdir -p "$O"
for v in "$@"; do
  ls "$P/$v"/scene_*.mp4 | sort | sed "s#^#file '#; s#\$#'#" > "$P/$v/list.txt"
  ffmpeg -y -loglevel error -f concat -safe 0 -i "$P/$v/list.txt" -c copy -movflags +faststart "$O/$v.mp4"
  echo "$v $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$O/$v.mp4")s"
done
