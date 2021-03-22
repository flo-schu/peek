#!/bin/bash

WORK=$1
DATE=$2
NANO=$3
mkdir -v "$WORK"/archives

# create slim directory with only csv files, which is sufficient for analysis
find "$WORK"/pics -type d -name "$DATE/$NANO" > /tmp/nano-archive.txt
echo "created file list /tmp/nano-archive.txt"
echo "processing /tmp/nano-archive.txt ..."
# tar -cfv "$WORK"/archives/"$DATE_$NANO".tar -T /tmp/nano-archive.txt
