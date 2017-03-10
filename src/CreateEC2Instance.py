from __future__ import print_function
import boto3

user_data_script = """#!/bin/bash -ex
S3_BUCKET=%s
DB_TABLE=jobs_by_uuid
REPO=https://github.com/glgerard/cloud-mdbn.git
mke2fs -t ext4 /dev/xvdk
USER_MP=/u01
mount ${USER_MP}
cd ${USER_MP}
git clone $REPO
chown -R ubuntu:ubuntu cloud-mdbn"""

ec2 = boto3.resource('ec2')

def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        ec2.create_instances(DryRun=False,
                             ImageId='ami-21cde547',
                             MinCount=1,
                             MaxCount=1,
                             KeyName='mykey',
                             SecurityGroups=['mdbnsecgroup'],
                             UserData=user_data_script % bucket,
                             InstanceType='t2.micro',
                             BlockDeviceMappings=[
                                 {
                                     "DeviceName": "/dev/sdk",
                                     "Ebs": {
                                         "VolumeSize": 16,
                                         "DeleteOnTermination": True,
                                         "VolumeType": "standard"
                                     }
                                 }
                             ],
                             InstanceInitiatedShutdownBehavior='terminate',
                             IamInstanceProfile={
                                 'Name': 'aws-ec2-mdbn'
                             }
                             )

