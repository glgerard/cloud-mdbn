#!/bin/bash
# Scan configuration JSON files in the CONFIG_DIR that begins with PREFIX
# convert them into a csv representation and appends them to a csv file.

TOOLS_DIR=${MDBN_ROOT}/tools
PREFIX=ov

if [ $# -ne 1 ]; then
    echo "Usage: $0 <config_dir>"
    exit -1
fi

CONF_DIR=$1

CWD=$(pwd)
cd ${CONF_DIR}
[ -f ${PREFIX}_configs.csv ] && rm ${PREFIX}_configs.csv

cat ${PREFIX}_configs_header.csv > ${PREFIX}_configs.csv

for json in $(ls ${PREFIX}_config*.json); do
    echo $json
    python ${TOOLS_DIR}/config_to_csv.py $json >> ${PREFIX}_configs.csv 
done
cd $CWD
