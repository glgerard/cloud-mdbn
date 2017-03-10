#!/usr/bin/env bash

if [ -z ${MDBN_ROOT} ]; then
    echo "Error: no MDBN_ROOT defined. Please source tools/env.sh."
fi

cwd=`pwd`
cd ${MDBN_ROOT}/src

# Initialization parameters

rolearn="arn:aws:iam::403237659795:role/lambda-s3-execution-role"
pkgname=CreateEC2Instance
region=eu-west-1
aws_profile=adminuser

echo "Create lambda function started. This will take a while..."

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

echo "Done."

cd $cwd