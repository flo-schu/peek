#!/bin/bash


target=/work/schunckf/nanocosm/data/pics/
echo $target

# remove files of different types
find $target -mindepth 5 -name "*.tiff" -print -exec rm {} \;
find $target -mindepth 5 -name "*.npy" -print -exec rm {} \;
find $target -mindepth 1 -name "*.jpeg" -print -exec rm {} \;
find $target -mindepth 1 -name "*.csv" -print -exec rm {} \;

# remove empty directories
find $target -empty -type d -delete
