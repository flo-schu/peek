#!/usr/bin/env bash
#SBATCH -D /work/%u
#SBATCH -J nanocosm_read
#SBATCH -t 0-01:00:00
#SBATCH --mem-per-cpu 10G 
#SBATCH -o /work/%u/logs/%x-%A-%a.out
#SBATCH -e /work/%u/logs/%x-%A-%a.err


for DATE in "$@"
do
    echo "processing Session ${DATE} ..."
    SESSION=$(find "data/pics/${DATE}/" -name "*.RW2" | sort -n)

    for image in $SESSION
        do 
            echo "processing $image ..."
            python "src/read_eve.py" "$image" -o jpeg -t TRUE
    done

    echo "forwarding QR errors."
    # copy qr errors:
    mkdir -p data/image_analysis/qr/${DATE}/qr_errors
    find "data/pics/${DATE}/999/" -type f -name "*_qr.jpeg" -print > "data/image_analysis/qr/${DATE}/qr_corrections.csv"
    cat "data/image_analysis/qr/${DATE}/qr_corrections.csv" | xargs cp -t "data/image_analysis/qr/${DATE}/qr_errors/"

done

