# Local installation

## Environment

Please make sure you are already using the following development environment or refer to
[INSTALL](doc/INSTALL.md) for detailed instructions on how to set it up.

* [Ubuntu 16.04 LTS](http://releases.ubuntu.com/16.04/)
* [Enthought Canopy](https://www.enthought.com/products/canopy/).
* In order to use GPU acceleration on your workstation you will have to install
[Nvidia CUDA 8.0](https://developer.nvidia.com/cuda-downloads) for Ubuntu 16.04.

Launch the Canopy Package Manager and install the following package
* flask

From a terminal run the following commands (make sure Canopy is your default
Python environment)

    sudo apt-get install git
    pip install boto3
    pip install Theano

## Check the installation works properly

From the root directory of the repository do the following.
This will create a run for the Ovarian cancer data

    source tools/env.sh
    cd config
    init_configs.sh ov ov_configs_2017_02_20_1133_init.csv
    cd ..
    python src/main.py -c config/ov_config_2_1.json -l -v
    
At the end of the 5 runs which take about 40 minutes to complete on a
i5-4690K CPU with a GeForce 1070 GPU, you will get the following
content in the directory `MDBN_run`

    MDBN_run/
    └── OV_Batch_c714f750448bae901740f8f2866f36ea
        ├── batch.log
        ├── Exp_c714f750448bae901740f8f2866f36ea_run_0.npz
        ├── Exp_c714f750448bae901740f8f2866f36ea_run_1.npz
        └── Exp_c714f750448bae901740f8f2866f36ea_run_2.npz
        └── Exp_c714f750448bae901740f8f2866f36ea_run_3.npz
        └── Exp_c714f750448bae901740f8f2866f36ea_run_4.npz

To monitor progress you can use the following command

    tail -f MDBN_run/OV_Batch_c714f750448bae901740f8f2866f36ea/batch.log
    
The data can be reviewed with a jupyter notebook. From the root directory of
the repository run

    jupyter notebook
    
Browse to the `notebooks` directory and open `OV-2_1.ipynb`.
    
# AWS EC2 installation

On a Unix like environment (Linux/macOS) install the AWS command line.
Refer to [Installing the AWS Command Line Interface](http://docs.aws.amazon.com/cli/latest/userguide/installing.html)
for details.

Make sure you have a Key pair named _mykey_ in your AWS account. Refer to
[Amazon EC2 Key Pairs](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html)
for instructions how to create the key pair.

Go to the root directory of the repository and run

    source tools/env.sh
    mkdir queue
    cd queue
    init_configs.sh ov ../config/ov_aws_init.csv
    sync_s3.sh . aws-your-bucket-name
    create_stack aws-your-bucket-name
    
Replace the string `aws-your-bucket-name` with a unique identifier of your choice.
This will be the S3 bucket where the results will be stored. It must be unique not to
conflict with other S3 buckets in the same AWS region. A good choice is to start this name
with the reverse DNS name of your institutional domain.

The last command will automatically launch a batch run of all the configuration
files under the `queue` directory on a t.micro EC2 instance .

You can also access the instance by running this command

    ssh -i ~/mykey.pem ubuntu@`get_aws_ec2.sh`

where I assumed that `~/mykey.pem` is the private key file associated to the
_mykey_ key pair.

Make sure to destroy the stack when you have finished your experiments with

    aws cloudformation delete-stack --stack-name mdbn

