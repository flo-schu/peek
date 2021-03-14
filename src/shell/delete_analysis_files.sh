#!/bin/bash

target=$1
echo $target

# remove files of different types
find $target -mindepth 1 -name "*.tiff" -exec rm {} \;
find $target -mindepth 1 -name "*.npy" -exec rm {} \;
find $target -mindepth 1 -name "*.json" -exec rm {} \;
find $target -mindepth 1 -name "*.csv" -exec rm {} \;

# remove empty directories
find $target -empty -type d -delete
