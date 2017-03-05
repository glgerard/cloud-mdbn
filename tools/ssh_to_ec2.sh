#!/usr/bin/env bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <path-to-key>"
    exit -1
fi

mykey=$1

ec2ip=$(aws ec2 describe-instances --filters "Name=tag:system,Values=mdbn" \
    --query "Reservations[0].Instances[0].PublicDnsName" | sed -e's/"//g')

ssh -i ${mykey} ubuntu@$ec2ip
