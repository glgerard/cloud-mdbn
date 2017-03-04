#!/usr/bin/env bash

# Setup the EC2 instance and start the batch

# Git repository
REPO=https://github.com/glgerard/cloud-mdbn.git

sudo apt-get -q -y install g++
sudo apt-get -q -y install python-qt4
sudo apt-get -q -y install awscli
sudo mkfs /dev/xvdk
sudo mkdir /mnt/db
sudo mount /dev/xvdk /mnt/db
sudo chown ubuntu:ubuntu /mnt/db
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
cd /mnt/db
git clone $REPO
cd cloud-mdbn
source tools/env.sh
aws s3 sync s3://${S3_BUCKET}/queue queue
python src/main.py -b config/queue -s ${S3_BUCKET} -y -l -v