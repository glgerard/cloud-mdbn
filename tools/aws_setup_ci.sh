#!/usr/bin/env bash

# Setup the EC2 instance and start the batch

# Git repository
REPO=https://github.com/glgerard/cloud-mdbn.git

sudo mke2fs -t ext4 /dev/xvdk
USER_MP=/u01
sudo mount ${USER_MP}
cd ${USER_MP}
git clone $REPO
sudo chown ubuntu:ubuntu cloud-mdbn
su ubuntu -c "cd ${USER_MP}/cloud-mdbn; tools/start_mdbn_cloud.sh OV ${S3_BUCKET}"