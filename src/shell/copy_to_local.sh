#!/usr/bin/env bash

DATE=`date +%Y%m%d`
echo $DATE
scp schunckf@frontend1.eve.ufz.de:/work/schunckf/nanocosm/data/qr_errors_$DATE.txt "./data/image_analysis/QR/qrcorrections/qr_errors_$DATE.txt"
scp schunckf@frontend1.eve.ufz.de:/work/schunckf/nanocosm/data/qr_errors_$DATE.tar "./data/image_analysis/QR/qr_errors_$DATE.tar"
