#!/bin/bash

#we must write the full path here (no ~ character)
target=$1
echo $target

for dir in "$target"/*/
do
    find $dir -mindepth 2 -type f -name "*.RW2" -print -exec mv {} $dir \;
    find $dir -empty -type d -delete
done
