#!/usr/bin/env bash

find "data/image_analysis/qr/" -mindepth 2 -name "qr_corrections.csv" | sort -n | xargs cat > "data/image_analysis/qr/qr_corrections.csv"

python src/qrcorrect.py "data/image_analysis/qr/qr_corrections.csv"

find data/pics/ -empty -type d -delete -print
find data/pics/*/999/ -type f -name "*.jpeg" > data/image_analysis/qr/qr_errors_unresolved.txt

# delete qr thumbnails
find data/pics/ -type f -name "*_qr.jpeg" -delete -print
