#!/usr/bin/env bash
DATE=`date +%Y%m%d`
mkdir /work/schunckf/nanocosm/data/qr/qr_errors_$DATE/
find /work/schunckf/nanocosm/data/pics/*/999/ -type f -name "*.jpeg" -print > /work/schunckf/nanocosm/data/qr/qr_errors_$DATE.txt
cat /work/schunckf/nanocosm/data/qr/qr_errors_$DATE.txt | xargs cp -t /work/schunckf/nanocosm/data/qr/qr_errors_$DATE/
tar -cvf /work/schunckf/nanocosm/data/qr/qr_errors_$DATE.tar /work/schunckf/nanocosm/data/qr/qr_errors_$DATE/