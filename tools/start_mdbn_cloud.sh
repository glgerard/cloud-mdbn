#!/usr/bin/env bash

# Start the MDBN network on an EC2 instance
# Receives a single parameter, the TCGA project either OV or LAML

if [ $# -ne 2 ]; then
    echo "Usage: $0 <OV|AML> <s3_bucket>"
    exit -1
fi

project=$1
s3bucket=$2

source tools/env.sh

aws s3 sync s3://${s3bucket}/queue queue

nohup /miniconda/bin/python src/main.py -t ${project} -b queue -s3 ${s3bucket} -y -l -v &