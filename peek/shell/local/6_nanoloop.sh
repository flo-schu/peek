SCRIPT=$1
id=1
while [ $id -le 80 ]
    do
    echo $id
    python ${SCRIPT} $id
    ((id++))
done