#!/usr/bin/env bash
INPUT_DIR=$1
SESSION=`ls -d $INPUT_DIR*/ | head -n $2 | tail -n 1`
SERIES=`ls -d $SESSION*/`
for i in $SERIES
    do echo $i

done
