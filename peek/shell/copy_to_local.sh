#!/usr/bin/env bash

DATE=`date +%Y%m%d`
echo $DATE

mkdir -p ./data/image_analysis/qr/$DATE
scp schunckf@frontend1.eve.ufz.de:/work/schunckf/nanocosm/data/qr/$DATE/qr_errors.txt "./data/image_analysis/qr/$DATE/qr_errors.txt"
scp schunckf@frontend1.eve.ufz.de:/work/schunckf/nanocosm/data/qr/$DATE/qr_errors.tar "./data/image_analysis/qr/$DATE/qr_errors.tar"

tar -C ./data/image_analysis/qr/$DATE/ -xvf ./data/image_analysis/qr/$DATE/qr_errors.tar 
mv ./data/image_analysis/qr/$DATE/work/schunckf/nanocosm/data/qr/$DATE/qr_errors ./data/image_analysis/qr/$DATE
cp ./data/image_analysis/qr/$DATE/qr_errors.txt ./data/image_analysis/qr/$DATE/qr_corrections.csv 
rm -rf ./data/image_analysis/qr/$DATE/work