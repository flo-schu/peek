
for DATE in "$@"
do
    echo "processing Session ${DATE} ..."
    mkdir "data/pics_classic/$DATE/"
    NANOS=$(find "data/pics/${DATE}/" -mindepth 1 -maxdepth 1 -type d | sort -n)

    NEWNAME=0
    for id in $NANOS
    do 
        echo "processing NANO ${id} ..."
        SERIES=$(find ${id} -mindepth 2 -maxdepth 2 -name "*.jpeg" | sort -n)

        i=0
        for image in $SERIES
        do
            echo "processing $image ... save to data/pics_classic/${DATE}/${NEWNAME}.jpeg"
            cp "${image}" "data/pics_classic/${DATE}/${NEWNAME}.jpeg"
            NEWNAME=$((NEWNAME+1))
            # breaks the loop after processing the first three images in one session
            if [[ $i -eq 2 ]]; then
                break
            fi
            i=$((i+1))
        done

    done
    echo "finished session."

done

