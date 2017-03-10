#!/usr/bin/env bash

# Initialization parameters

region=eu-west-1
aws_profile=adminuser
bucketOwner="403237659795"
rolearn="arn:aws:iam::${bucketOwner}:role/lambda-s3-execution-role"

if [ -z ${MDBN_ROOT} ]; then
    echo "Error: no MDBN_ROOT defined. Please source tools/env.sh."
fi

if [ $# -ne 2 ]; then
    echo "Usage: $0 <pkgname> <s3-bucket>"
    exit -1
fi

pkgname=$1
sourcebucket=$2

cwd=`pwd`
cd ${MDBN_ROOT}/src

echo "Create lambda function started. This will take a while..."

#
if [ `aws lambda list-functions --query 'Functions[*].FunctionName' | \
        grep \"$pkgname\" | wc -l` -ne 1 ]; then
    aws lambda create-function \
    --region $region \
    --function-name $pkgname \
    --zip-file fileb://${pkgname}.zip \
    --role ${rolearn} \
    --handler ${pkgname}.handler \
    --runtime python2.7 \
    --profile $aws_profile \
    --timeout 10 \
    --memory-size 1024
fi

aws lambda add-permission \
--function-name $pkgname \
--region $region \
--statement-id "$pkgname-id-001" \
--action "lambda:InvokeFunction" \
--principal s3.amazonaws.com \
--source-arn arn:aws:s3:::${sourcebucket} \
--source-account $bucketOwner \
--profile $aws_profile

echo "Done."

cd $cwd