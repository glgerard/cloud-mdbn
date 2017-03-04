# Local installation

## Environment

Please make sure you are already using the following development environment or
refer to [INSTALL](INSTALL.md) for detailed instructions on how to set it up.

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
    python src/main.py -t OV -c config/ov_config_20_1_05.json -l -v

The first time you run the command you will obtain the following message

    Downloading TCGA_Data from https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3479191/bin/

This is normal as we are downloading the original data for the first run.

At the end of the 5 runs which take about 50 minutes to complete on a
i5-4690K CPU with a GeForce 1070 GPU, you will get the following
content in the directory `MDBN_run`

    OV_Batch_73dab4ea3383b2666d1220969a7feba8/
    ├── batch.log
    ├── Exp_73dab4ea3383b2666d1220969a7feba8_run_0.npz
    ├── Exp_73dab4ea3383b2666d1220969a7feba8_run_1.npz
    ├── Exp_73dab4ea3383b2666d1220969a7feba8_run_2.npz
    ├── Exp_73dab4ea3383b2666d1220969a7feba8_run_3.npz
    ├── Exp_73dab4ea3383b2666d1220969a7feba8_run_4.npz
    └── ov_config_20_1_05.json

To monitor progress you can use the following command

    tail -f ${MDBN_ROOT}/MDBN_run/OV_Batch_c714f750448bae901740f8f2866f36ea/batch.log
    
The data can be reviewed with a Jupyter notebook. From the root directory of
the repository run

    jupyter notebook
    
Browse to the `notebooks` directory and open `View-OV-20_1_05.ipynb`.

You can now test a run with AML data. To do this execute the following commands

    cd ${MDBN_ROOT}/config
    init_configs.sh aml aml_configs_2017_02_20_2050_init.csv
    cd ..
    python src/main.py -t AML -c config/aml_config_20_1_05.json -l -v
    
At the end of the 4 runs you will get the following new content under `MDBN_run`

    AML_Batch_eb6856a251bb8680da6593de98db7b5a/
    ├── aml_config_20_1_05.json
    ├── batch.log
    ├── Exp_eb6856a251bb8680da6593de98db7b5a_run_0.npz
    ├── Exp_eb6856a251bb8680da6593de98db7b5a_run_1.npz
    ├── Exp_eb6856a251bb8680da6593de98db7b5a_run_2.npz
    └── Exp_eb6856a251bb8680da6593de98db7b5a_run_3.npz
    
As before progress can be monitored via
    
    tail -f ${MDBN_ROOT}/MDBN_run/AML_Batch_eb6856a251bb8680da6593de98db7b5a/batch.log
    
The data can be reviewied instead via the Jupyter notebook. In case you have stopped
it restart as before and open the notebook `notebooks/View-AML-20_1_05.ipynb`.

# AWS EC2 installation

On a Unix like environment (Linux/macOS) install the AWS command line.
The easiest way to do it is by running

    pip install awscli
    
You will then have to setup your credentials by running

    aws configure

Refer to [Installing the AWS Command Line Interface](http://docs.aws.amazon.com/cli/latest/userguide/installing.html)
for details.

Make sure you have a Key pair named _mykey_ in your AWS account. Refer to
[Amazon EC2 Key Pairs](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html)
for instructions how to create the key pair.

Make sure that you have `boto3` installed as a python module
(if unsure run from the command line `pip install boto3`).

Now go to the root directory of the repository and first set the `S3_BUCKET` variable
to a unique AWS bucket name of your choice

    S3_BUCKET=your-bucket-name
    
You can now create a stack and launch a batch of configurations with the
following commands

    source tools/env.sh
    mkdir queue
    cd queue
    init_configs.sh ov ../config/ov_aws_init.csv
    sync_s3.sh . $S3_BUCKET
    create_stack $S3_BUCKET
    
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

When you have finished your experiments make sure to destroy the stack 

    aws cloudformation delete-stack --stack-name mdbn

