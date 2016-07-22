#!/bin/bash
filename="$1"
while read -r line
do
    oid=(${line// = / })
    number=$(snmptranslate -On -IR -m ALL $oid)
    if [ $? -eq 0 ]; then
        len=${#oid}
        echo $number${line:$len}
    else
        echo $line
        exit
    fi

done < "$filename"



#fd=3
#while IFS='' read -u $fd -r line || [[ -n "$line" ]]; do
#    split=(${IN// = / })
#    echo $split
#    echo $(snmptranslate -On -IR $oid)
#    echo "Text read from file: $line"
#done $fd< "$1"

