#!/usr/bin/env bash
# Initialize the S3 bucket to store the configuration files for batch execution

if [ -z "${S3ID}" ]; then
    echo "Error: S3ID not defined. Please source env.sh"
    exit -1
fi

BucketName=unipv-mdbn-$S3ID

aws s3 mb s3://${BucketName}/queue

# TODO: Set the permissions appropriately

aws s3api put-bucket-policy --bucket $BucketName \
--policy file://${MDBN_ROOT}/tools/bucket_policy.json
