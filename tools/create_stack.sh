#!/usr/bin/env bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 <s3_bucket> <cloudformation.json"
    exit -1
fi

if [ -z "${MDBN_ROOT}" ]; then
    echo "Error: MDBN_ROOT not defined. Please source env.sh"
    exit -1
fi

s3bucket=$1
cf_config_file=$2

aws s3 cp ${MDBN_ROOT}/tools/${cf_config_file} s3://${s3bucket}

region=$(aws configure get region)

az=$(aws ec2 describe-availability-zones \
    --query 'AvailabilityZones[0].ZoneName' --output text)
vpc=$(aws ec2 describe-vpcs --filter "Name=isDefault, Values=true" \
    --query "Vpcs[0].VpcId" --output text)
subnet=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$vpc,Name=availabilityZone,Values=$az" \
    --query Subnets[0].SubnetId --output text)

aws cloudformation create-stack --stack-name mdbn \
    --capabilities CAPABILITY_IAM --template-url \
https://s3-${region}.amazonaws.com/${s3bucket}/${cf_config_file} \
    --parameters \
            ParameterKey=KeyName,ParameterValue=mykey \
            ParameterKey=AvZone,ParameterValue=$az \
            ParameterKey=VPC,ParameterValue=$vpc \
            ParameterKey=Subnet,ParameterValue=$subnet \
            ParameterKey=S3Bucket,ParameterValue=$s3bucket \
            ParameterKey=DynamoDBTable,ParameterValue=jobs

while [[ `aws cloudformation describe-stacks --stack-name mdbn --query Stacks[0].StackStatus` != *"COMPLETE"* ]]
do
	sleep 10
done
aws cloudformation describe-stacks --stack-name mdbn --query Stacks[0].Outputs