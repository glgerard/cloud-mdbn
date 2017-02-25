#!/usr/bin/env bash
# Sync configuration files on S3

if [ -z "${S3ID}" ]; then
    echo "Error: S3ID not defined. Please source env.sh"
    exit -1
fi

if [ $# -ne 1 ]; then
    echo "Usage: $0 <batch_dir>"
    exit -1
fi

batch_dir=$1

aws s3 sync --dryrun $batch_dir s3://unipv-mdbn-${S3ID}/queue
