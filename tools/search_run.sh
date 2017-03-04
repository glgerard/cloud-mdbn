#!/usr/bin/env bash
# Search the batch directory with the results of a particular configuration
# Receives as input the search pattern which is typically a portion of the
# short name of the configuration file

if [ -z "${MDBN_ROOT}" ]; then
    echo "Error: MDBN_ROOT not defined. Please source env.sh"
    exit -1
fi

CONF_DIR=${MDBN_ROOT}/config
MDBN_RUN=${MDBN_ROOT}/MDBN_run

if [ $# -ne 2 ]; then
    echo "Usage: $0 <ov|aml> <pattern>"
    exit -1
fi

project=$1
pattern=$2

grep $pattern ${CONF_DIR}/${project}_configs.csv | awk -F',' -v count=1 '{print count++,")",$1,$(NF)}'
matches=$(grep $pattern ${CONF_DIR}/${project}_configs.csv | awk -F',' '{print $(NF)}')

echo
echo -n "Choose config file: "
read choice

uuid=$(echo $matches | awk -v choice=$choice '{print $(choice)}')
echo

find ${MDBN_RUN} -name batch.log -exec grep $uuid {} \; -ls
