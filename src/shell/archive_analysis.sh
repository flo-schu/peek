#!/bin/bash

DATE=`date +%Y%m%d_%H%M`

WORK=/work/schunckf/nanocosm/data/
ANALYSIS=$1
echo "archiving analysis $ANALYSIS in $WORK/pics"
mkdir -v "$WORK"/analyses

# create slim directory with only csv files, which is sufficient for analysis
SLIM="$ANALYSIS"-"$DATE"-slim
find "$WORK"/pics -name *.json > /tmp/nano-$SLIM.txt
find "$WORK"/pics -name *"$ANALYSIS"*.csv >> /tmp/nano-$SLIM.txt
echo "created file list /tmp/nano-$SLIM.txt"
echo "processing /tmp/nano-$SLIM.txt ..."
tar -cf "$WORK"/analyses/"$SLIM".tar -T /tmp/nano-$SLIM.txt

# # # create complete tar archive with tiff and npy files (BIG!!!)
# COMPLETE="$ANALYSIS"-"$DATE"-complete
# find "$WORK"/pics -name *"$ANALYSIS"* > /tmp/nano-"$COMPLETE"
# echo "created file list /tmp/nano-$COMPLETE.txt"
# echo "processing /tmp/nano-$COMPLETE.txt ..."
# tar -cf "$WORK"/analyses/"$COMPLETE".tar -T /tmp/nano-$COMPLETE.txt
