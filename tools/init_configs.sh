#!/bin/bash

# Take an initialization csv from Excel and create a new ov_configs.csv
# with standard format to be used by batch_run.py

CONF_DIR=../config
SRC_DIR=../src

init=$1

sed -e's/;/,/g' $init > ov_configs_tmp.csv
python ${SRC_DIR}/csv_to_config.py ov_configs_tmp.csv ${CONF_DIR}/ov_config_template.json
mv *.json ${CONF_DIR}
./scan_configs.sh ${CONF_DIR}
rm ov_configs_tmp.csv
