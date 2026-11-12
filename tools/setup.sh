#!/bin/bash
# Installs everything a render machine needs (GitHub runner or local Linux).
set -e
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg libcairo2-dev pkg-config fontconfig >/dev/null
pip install -q -r requirements.txt
mkdir -p ~/.local/share/fonts && cp assets/fonts/*.ttf ~/.local/share/fonts/ && fc-cache -f >/dev/null
