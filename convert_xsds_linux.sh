#!/bin/bash
generateds="./generateDS/generateDS.py"
destination="./information_model"
for filepath in artifacts/*.xsd
do
    echo $filepath
    name=${filepath##*/}
    base=${name%.xsd}
    python $generateds -o $destination/$base.py --export="write etree validate generator" -q -f --silence $filepath
done