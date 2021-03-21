#!/bin/bash

DATE=`date +%Y%m%d_%H%M`

WORK=/work/schunckf/nanocosm/data/
ANALYSIS=$1
echo "archiving analysis $ANALYSIS in $WORK/pics"
mkdir -v "$WORK"/analyses

# create slim directory with only csv files, which is sufficient for analysis
CSV="$ANALYSIS"-"$DATE"-csv
find "$WORK"/pics -name *"$ANALYSIS"*.csv > /tmp/nano-$CSV.txt
echo "created file list /tmp/nano-$CSV.txt"
echo "processing /tmp/nano-$CSV.txt ..."
tar -cf "$WORK"/analyses/"$CSV".tar -T /tmp/nano-$CSV.txt

# create complete tar archive with tiff and npy files (BIG!!!)
COMPLETE="$ANALYSIS"-"$DATE"-complete
find "$WORK"/pics -name *"$ANALYSIS"* > /tmp/nano-"$COMPLETE"
echo "created file list /tmp/nano-$COMPLETE.txt"
echo "processing /tmp/nano-$COMPLETE.txt ..."
tar -cf "$WORK"/analyses/"$COMPLETE".tar -T /tmp/nano-$COMPLETE.txt
