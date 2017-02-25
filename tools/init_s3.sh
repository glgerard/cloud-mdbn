#!/usr/bin/env bash
# Initialize the S3 bucket to store the configuration files for batch execution

if [ -z "${S3ID}" ]; then
    echo "Error: S3ID not defined. Please source env.sh"
    exit -1
fi

aws s3 mb s3://unipv-mdbn-$S3ID/queue

# TODO: Set the permissions appropriately

