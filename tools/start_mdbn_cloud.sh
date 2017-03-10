#!/usr/bin/env bash

# Start the MDBN network on an EC2 instance
# Receives two parameters
#   the TCGA project either OV or LAML
#   the S3 bucket name

if [ $# -ne 2 ]; then
    echo "Usage: $0 <OV|AML> <s3_bucket>"
    exit -1
fi

project=$1
s3bucket=$2
timestamp=$(date -u "+%Y%m%dT%H%M%S")

source tools/env.sh

aws s3 mv s3://${s3bucket}/payload/payload.zip payload.zip

unzip payload.zip

nohup sudo tools/spot_monitor.sh &

# nohup /miniconda/bin/python src/main.py -y -v -t ${project} -b payload -s3 ${s3bucket} -i ${timestamp} &