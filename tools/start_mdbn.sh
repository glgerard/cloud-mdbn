#!/bin/bash
# Start the MDBN network in deamon node
# Receives a single parameter, the TCGA project either OV or LAML

if [ $# -ne 1 ]; then
    echo "Usage: $0 <OV|AML>"
    exit -1
fi

project=$1

cd ${MDBN_ROOT}
${HOME}/Enthought/Canopy_64bit/User/bin/python src/main.py -t $project -d -v
