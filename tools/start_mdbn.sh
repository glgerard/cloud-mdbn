#!/bin/bash
# Start the MDBN network in deamon node
# Receives a single parameter, the TCGA project either OV or LAML

MDBN_ROOT=${HOME}/SoftwareProjects/Thesis/cloud-mdbn

if [ $# -ne 1 ]; then
    echo "Usage: $0 <OV|LAML>"
    exit -1
fi

project=$1

cd ${MDBN_ROOT}
${HOME}/Enthought/Canopy_64bit/User/bin/python src/main.py -d -v
