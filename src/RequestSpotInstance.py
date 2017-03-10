from __future__ import print_function
import boto3
from datetime import datetime
import uuid
import json

user_data_script = '''#!/bin/bash -ex
S3_BUCKET=%s
DB_TABLE=jobs_by_uuid
REPO=https://github.com/glgerard/cloud-mdbn.git
mke2fs -t ext4 /dev/xvdk
USER_MP=/u01
mount ${USER_MP}
cd ${USER_MP}
git clone $REPO
chown -R ubuntu:ubuntu cloud-mdbn
su ubuntu -c "(cd ${USER_MP}/cloud-mdbn; tools/start_mdbn_cloud.sh OV ${S3_BUCKET})"
'''

client = boto3.client('ec2')
s3_client = boto3.client('s3')

def handler(event, context):
    today = datetime.now()
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
        s3_client.download_file(bucket, key, download_path)
        with open(download_path) as fp:
            config = json.load(fp)
        response = client.request_spot_instances(DryRun=False,
                                                 SpotPrice=config['spot_price'],
                                                 InstanceCount=1,
                                                 Type='one-time',
                                                 ValidFrom=today,
                                                 ValidUntil=today+datetime.timedelta(days=1),
                                                 BlockDurationMinutes=60,
                                                 LaunchSpecification={
                                                     'ImageId': 'ami-e3f7c285',
                                                     'KeyName': 'mykey',
                                                     'SecurityGroups': ['mdbnsecgroup'],
                                                     'UserData': user_data_script % bucket,
                                                     'InstanceType': config['instance_type'],
                                                     'BlockDeviceMappings': [
                                                         {
                                                             "DeviceName": "/dev/sdk",
                                                             "Ebs": {
                                                                 "VolumeSize": 16,
                                                                 "DeleteOnTermination": True,
                                                                 "VolumeType": "standard"
                                                             }
                                                         }
                                                     ],
                                                     'IamInstanceProfile': {
                                                         'Name': 'aws-ec2-mdbn'
                                                     }
                                                 }
                                                 )
