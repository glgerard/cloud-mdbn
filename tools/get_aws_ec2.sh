#!/usr/bin/env bash

aws ec2 describe-instances --filters "Name=tag:system,Values=mdbn" --query "Reservations[0].Instances[0].PublicDnsName"
