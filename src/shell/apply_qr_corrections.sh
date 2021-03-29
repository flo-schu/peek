#!/usr/bin/env bash

PROJECT_DIR="/home/$USER/projects/nanocosm/"
WORKDIR="/work/$USER/nanocosm/data/"
source "$PROJECT_DIR/env/bin/activate"

find $WORKDIR/qr/ -mindepth 2 -name "qr_corrections.csv" | sort -n | xargs cat > $WORKDIR/qr/qr_corrections.csv

python $PROJECT_DIR/src/qrcorrect.py $WORKDIR/qr/qr_corrections.csv

find $WORKDIR/pics/ -empty -type d -delete -print
find $WORKDIR/pics/*/999/ -type f -name "*.tiff" > $WORKDIR/qr/qr_errors_unresolved.txt

unset PROJECT_DIR
unset WORKDIR