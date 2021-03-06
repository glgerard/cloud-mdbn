#!/usr/bin/env bash
# Scan configuration JSON files in the CONFIG_DIR that begins with PREFIX
# convert them into a csv representation and appends them to a csv file.

if [ -z "${MDBN_ROOT}" ]; then
    echo "Error: MDBN_ROOT not defined. Please source env.sh"
    exit -1
fi

CONF_DIR=${MDBN_ROOT}/config
TOOLS_DIR=${MDBN_ROOT}/tools

if [ $# -ne 2 ]; then
    echo "Usage: $0 <ov|aml> <config_dir>"
    exit -1
fi

PREFIX=$1
JSON_DIR=$2

CWD=$(pwd)
cd ${JSON_DIR}
[ -f ${PREFIX}_configs.csv ] && rm ${PREFIX}_configs.csv

cat ${CONF_DIR}/${PREFIX}_configs_header.csv > ${PREFIX}_configs.csv

for json in $(ls ${PREFIX}_config*.json); do
    echo $json
    python ${TOOLS_DIR}/config_to_csv.py $json >> ${PREFIX}_configs.csv 
done
cd $CWD
