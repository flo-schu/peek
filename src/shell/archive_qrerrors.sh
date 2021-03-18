#!/usr/bin/env bash

mkdir /work/schunckf/nanocosm/data/qr_errors/
find /work/schunckf/nanocosm/data/pics/*/999/ -type f -name "*.jpeg" -print > /work/schunckf/nanocosm/data/qr_errors.txt
cat /work/schunckf/nanocosm/data/qr_errors.txt | xargs cp -t /work/schunckf/nanocosm/data/qr_errors/
tar -cvf /work/schunckf/nanocosm/data/qr_errors.tar /work/schunckf/nanocosm/data/qr_errors/