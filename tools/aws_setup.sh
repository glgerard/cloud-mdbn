#!/usr/bin/env bash

# Setup the EC2 instance and start the batch

sudo apt install g++
wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda
source $HOME/miniconda/bin/activate
pip install --upgrade --user awscli
conda install -y -q boto3
conda install -y -q numpy
conda install -y -q scipy
conda install -y -q theano
conda install -y -q pyqt
conda install -y -q matplotlib
conda install -y -q flask
sudo apt install python-qt4
git clone https://github.com/glgerard/cloud-mdbn.git
cd cloud-mdbn/
source tools/env.sh
aws s3 sync s3://unipv-mdbn-ggerard/queue queue
python src/main.py -b config/queue -s unipv-mdbn-ggerard -l -v