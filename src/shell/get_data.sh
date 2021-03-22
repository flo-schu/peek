#!usr/bin/env bash

# set this variables once to access files (omit ending slash)
DATA_REMOTE="/work/schunckf/nanocosm/data"
DATA_LOCAL="C:/Users/schunckf/Documents/Florian/papers/nanocosm/data"

# Parse variables
for i in "$@"
do
case $i in
    -d=*|--date=*)
    DATE="${i#*=}"
    shift # past argument=value
    ;;
    -n=*|--nanocosm=*)
    NANO="${i#*=}"
    shift # past argument=value
    ;;
esac
done

# provide default values
TARFILE="$DATE"_"$NANO".tar

DATE=${DATE:-*}
NANO=${NANO:-*}

echo "getting data from $DATA_REMOTE/pics/$DATE/$NANO and storing output in $TARFILE"
echo "This might take a while ..."

# create archive on remote and download
ssh schunckf@frontend1.eve.ufz.de tar -cf "$DATA_REMOTE"/archives/$TARFILE "$DATA_REMOTE"/pics/"$DATE"/"$NANO"/
scp schunckf@frontend1.eve.ufz.de:"$DATA_REMOTE"/archives/"$TARFILE" "$DATA_LOCAL"/pics/

# extract archive on local machine and remove archive
echo "extracting the archive"
tar -C "$DATA_LOCAL"/pics/ -xf "$DATA_LOCAL"/pics/"$TARFILE"
mv "$DATA_LOCAL"/pics/"$DATA_REMOTE"/pics/$DATE/ "$DATA_LOCAL"/pics/
rm -rf "$DATA_LOCAL"/pics/work/
rm "$DATA_LOCAL"/pics/"$TARFILE"

# remove variables from shell
unset DATE
unset NANO
unset TARFILE
unset DATA_LOCAL
unset DATA_REMOTE
