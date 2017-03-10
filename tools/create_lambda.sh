#!/usr/bin/env bash

rolearn="arn:aws:iam::403237659795:role/lambda-s3-execution-role"

aws lambda create-function \
--region eu-west-1 \
--function-name CreateEC2Instance \
--zip-file fileb://CreateEC2Instance.zip \
--role ${rolearn} \
--handler CreateEC2Instance.handler \
--runtime python2.7 \
--profile adminuser \
--timeout 10 \
--memory-size 1024