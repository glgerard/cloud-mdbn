#!/bin/bash
# Search the batch directory with the results of a particular configuration
# Receives as input the search pattern which is typically a portion of the
# short name of the configuration file

if [ $# -ne 1 ]; then
    echo "Usage: $0 <patter>"
    exit -1
fi

pattern=$1

grep $pattern ov_configs.csv | awk -F',' -v count=1 '{print count++,")",$1,$(NF)}'
matches=$(grep $pattern ov_configs.csv | awk -F',' '{print $(NF)}')

echo
echo -n "Choose config file: "
read choice

uuid=$(echo $matches | awk -v choice=$choice '{print $(choice)}')
echo

find ../MDBN_run -name batch.log -exec grep $uuid {} \; -ls
