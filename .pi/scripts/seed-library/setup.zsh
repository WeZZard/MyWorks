#!/usr/bin/env zsh
# Install the dezoomify-rs binary (downloads zoomable images from Google Art
# Project). The binary is gitignored; run this once on a fresh clone.
set -euo pipediff 2>/dev/null || set -eu
HERE="${0:A:h}"
cd "$HERE"
TAG="v2.18.0"
URL="https://github.com/lovasoa/dezoomify-rs/releases/download/${TAG}/dezoomify-rs-macos.tgz"
echo ">> downloading dezoomify-rs ${TAG}"
curl -sL -o dz.tgz "$URL"
tar xzf dz.tgz
rm -f dz.tgz
./dezoomify-rs --version
echo ">> done. recall seeds with: python3 recall.py <style>"