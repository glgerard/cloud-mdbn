#!/bin/bash

# Scan configuration JSON files in the CONFIG_DIR that begins with PREFIX
# convert them into a csv representation and appends them to a csv file.

CONF_DIR=../config
PREFIX=ov

[ -f ${CONF_DIR}/${PREFIX}_configs.csv ] && rm ${CONF_DIR}/${PREFIX}_configs.csv

cat ${CONF_DIR}/${PREFIX}_configs_header.csv > ${CONF_DIR}/${PREFIX}_configs.csv

for json in $(ls ${CONF_DIR}/${PREFIX}_config*.json); do
    echo $json
    python config_to_csv.py $json >> ${CONF_DIR}/${PREFIX}_configs.csv 
done
