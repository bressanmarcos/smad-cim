#!/bin/bash
# cimrdf.py e generateDS devem estar instalados
origin="./artifacts"
destination="./information_model"
for filepath in $origin/*.xsd
do
    name=${filepath##*/}
    base=${name%.xsd}
    echo "$filepath --> $destination/$base.py" 
    generateDS -o $destination/$base.py --export="write etree validate generator" -q -f --silence $filepath
done