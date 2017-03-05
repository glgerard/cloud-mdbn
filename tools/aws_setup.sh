#!/usr/bin/env bash

# Setup the EC2 instance and start the batch

# Git repository
REPO=https://github.com/glgerard/cloud-mdbn.git

sudo apt-get -q -y install g++
sudo apt-get -q -y install python-qt4
sudo apt-get -q -y install awscli
sudo mke2fs -t ext4 /dev/xvdk
USER_MP=/u01
sudo mkdir ${USER_MP}
echo "/dev/xvdk		${USER_MP}	 ext4	defaults,discard	0 0" >> /etc/fstab
sudo mount ${USER_MP}
wget -q https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda
source $HOME/miniconda/bin/activate
#pip install --quiet --upgrade --user awscli
conda install -y -q boto3
conda install -y -q numpy
conda install -y -q scipy
conda install -y -q theano
conda install -y -q pyqt
conda install -y -q matplotlib
conda install -y -q flask
conda install -y -q requests
cd ${USER_MP}
git clone $REPO
sudo chown ubuntu:ubuntu cloud-mdbn
su ubuntu -c "cd ${USER_MP}/cloud-mdbn; tools/start_mdbn_cloud.sh OV ${S3_BUCKET}"
