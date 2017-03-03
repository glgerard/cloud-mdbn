#!/usr/bin/env bash
# Sync configuration files on S3

if [ $# -ne 2 ]; then
    echo "Usage: $0 <batch_dir> <s3_bucket>"
    exit -1
fi

batch_dir=$1
s3_bucket=$2

aws s3 sync $batch_dir s3://${s3_bucket}/queue
