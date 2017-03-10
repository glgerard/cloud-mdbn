#!/usr/bin/env bash
# Initialize the S3 bucket to store the configuration files for batch execution

if [ -z "${S3BUCKET}" ]; then
    echo "Error: S3BUCKET not defined. Please source tools/env.sh"
    exit -1
fi

BucketName=$S3BUCKET

aws s3 mb s3://${BucketName}/queue

# TODO: Set the permissions appropriately

aws s3api put-bucket-policy --bucket $BucketName \
--policy file://${MDBN_ROOT}/tools/bucket_policy.json
