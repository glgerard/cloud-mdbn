#!/usr/bin/env bash
# Take an initialization csv from Excel and create a new ov_configs.csv
# with standard format to be used by batch_run.py

if [ -z "${MDBN_ROOT}" ]; then
    echo "Error: MDBN_ROOT not defined. Please source env.sh"
    exit -1
fi

CONF_DIR=${MDBN_ROOT}/config
SRC_DIR=${MDBN_ROOT}/src
TOOLS_DIR=${MDBN_ROOT}/tools

if [ $# -ne 2 ]; then
    echo "Usage: $0 <ov|aml> <config.csv>"
    exit -1
fi

project=$1
initcsv=$2

sed -e's/;/,/g' $initcsv > ${project}_configs_tmp.csv
python ${SRC_DIR}/csv_to_config.py ${project}_configs_tmp.csv ${CONF_DIR}/${project}_template.json
${TOOLS_DIR}/scan_configs.sh ${project} .
rm ${project}_configs_tmp.csv
