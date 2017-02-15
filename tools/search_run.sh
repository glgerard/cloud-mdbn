#!/bin/bash

pattern=$1

grep $pattern ov_configs.csv | awk -F',' -v count=1 '{print count++,")",$1,$(NF)}'
matches=$(grep $pattern ov_configs.csv | awk -F',' '{print $(NF)}')

echo
echo -n "Choose config file: "
read choice

uuid=$(echo $matches | awk -v choice=$choice '{print $(choice)}')
echo

find ../MDBN_run -name batch.log -exec grep $uuid {} \; -ls
