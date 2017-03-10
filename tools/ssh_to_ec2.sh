#!/usr/bin/env bash

NETCAT=nc

function check_ssh {
    $NETCAT -z -G 5 $1 22
    return $?
}

if [ $# -ne 1 ]; then
    echo "Usage: $0 <path-to-key>"
    exit -1
fi

mykey=$1

ec2ip=$(aws ec2 describe-instances --filters "Name=tag:system,Values=mdbn" \
    --query "Reservations[0].Instances[0].PublicDnsName" | sed -e's/"//g')

# Wait for the SSH port to be available

echo "Wait for the IP network to come up"
while [[ `check_ssh $ec2ip` -eq 1 ]]; do
    echo -n "."
    sleep 5
done

ssh -i ${mykey} ubuntu@$ec2ip
