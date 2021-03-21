#!/usr/bin/env bash
DATE=`date +%Y%m%d`
rm -rf /work/schunckf/nanocosm/data/qr/$DATE/
mkdir -p /work/schunckf/nanocosm/data/qr/$DATE/qr_errors/
find /work/schunckf/nanocosm/data/pics/*/999/ -type f -name "*.jpeg" -print > /work/schunckf/nanocosm/data/qr/$DATE/qr_errors.txt
cat /work/schunckf/nanocosm/data/qr/$DATE/qr_errors.txt | xargs cp -t /work/schunckf/nanocosm/data/qr/$DATE/qr_errors/
tar -cvf /work/schunckf/nanocosm/data/qr/$DATE/qr_errors.tar /work/schunckf/nanocosm/data/qr/$DATE/qr_errors/