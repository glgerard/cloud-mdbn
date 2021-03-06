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
    python src/main.py -t OV -c config/ov_config_20_1_05.json -l -v -i 20170220T114308

The first time you run the command you will obtain the following message

    Downloading TCGA_Data from https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3479191/bin/

This is normal as we are downloading the original data for the first run.

At the end of the 5 runs which take about 50 minutes to complete on a
i5-4690K CPU with a GeForce 1070 GPU, you will get the following
content in the directory `MDBN_run`

    OV_Batch_20170220T114308/
    ├── Exp_73dab4ea3383b2666d1220969a7feba8_run_0.npz
    ├── Exp_73dab4ea3383b2666d1220969a7feba8_run_1.npz
    ├── Exp_73dab4ea3383b2666d1220969a7feba8_run_2.npz
    ├── Exp_73dab4ea3383b2666d1220969a7feba8_run_3.npz
    ├── Exp_73dab4ea3383b2666d1220969a7feba8_run_4.npz
    ├── ov_config_20_1_05.json
    ├── run.0.og
    ├── run.1.og
    ├── run.2.og
    ├── run.3.og
    └── run.4.og

To monitor progress, for example, of the first run you can use the
following command

    tail -f ${MDBN_ROOT}/MDBN_run/OV_Batch_20170220T114308/run.0.log
    
The data can be reviewed with a Jupyter notebook. From the root directory of
the repository run

    jupyter notebook
    
Browse to the `notebooks` directory and open `View-OV-20_1_05.ipynb`.

You can now test a run with AML data. To do this execute the following commands

    cd ${MDBN_ROOT}/config
    init_configs.sh aml aml_configs_2017_02_20_2050_init.csv
    cd ..
    python src/main.py -t AML -c config/aml_config_20_1_05.json -l -v -i 20170220T205506
    
At the end of the 4 runs you will get the following new content under `MDBN_run`

    AML_Batch_20170220T205506/
    ├── aml_config_20_1_05.json
    ├── Exp_eb6856a251bb8680da6593de98db7b5a_run_0.npz
    ├── Exp_eb6856a251bb8680da6593de98db7b5a_run_1.npz
    ├── Exp_eb6856a251bb8680da6593de98db7b5a_run_2.npz
    ├── Exp_eb6856a251bb8680da6593de98db7b5a_run_3.npz
    ├── run.0.log
    ├── run.1.log
    ├── run.2.log
    └── run.3.og
    
As before progress, for example, of the first run can be monitored via
    
    tail -f ${MDBN_ROOT}/MDBN_run/AML_Batch_20170220T205506/run.0.log

The data can be reviewed instead via the Jupyter notebook. In case you have stopped
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
    create_stack $S3_BUCKET server-cloudformation.json
    
Replace the string `aws-your-bucket-name` with a unique identifier of your choice.
This will be the S3 bucket where the results will be stored. It must be unique not to
conflict with other S3 buckets in the same AWS region. A good choice is to start this name
with the reverse DNS name of your institutional domain.

The last command will automatically launch a batch run of all the configuration
files under the `queue` directory on a t.micro EC2 instance .

You can also connect to the instance with this command

    ssh_to_ec2.sh ~/mykey.pem

where I assumed that `~/mykey.pem` is the private key file associated to the
_mykey_ key pair.

You can check the status of the initialization by looking at the file

    tail -20 /var/log/cloud-init-output.log

The run data should be stored in the directory called `/u01/cloud-mdbn/MDBN_run`.

If everything worked as expected the data will now be uploaded
on the S3 bucket you previously defined.

When you have finished your experiments make sure to destroy the stack 

    aws cloudformation delete-stack --stack-name mdbn

### Custom image

The Cloudformation stack you created previously start from a plain vanilla
Ubuntu 16.04 install and every time you create the stack the
miniconda and Theano environment is installed.

Once you have the EC2 instance running you can also easily
create a custom image for future reuse. If you do so you
can just change the following section in `tools/server-cf-ci.json`

    "Mappings": {
        "EC2RegionMap": {
            "eu-west-1": {
            "MinicondaTheanoUbuntuXenial64bit": "ami-21cde547"
        }
    }

and replace the string `ami-21cde547` with the identifier of
the image you just created.

If you do so then the stack can be launched with

    create_stack $S3_BUCKET server-cf-ci.json

This will use the custom image effectively skipping the initial
lenghty process of downloading and installing the full
miniconda environment with Theano.