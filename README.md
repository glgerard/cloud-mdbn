# MDBN

A Theano implementation of a Multimodal Deep Belief Network used for clustering
two types of TCGA tumoral genetic data: Ovarian cancer and Acute Myeloid Leukemia (AML).

The network architecture and tuning hyperparameters are configured with a JSON file.

Once you have cloned the repository the analysis can be started interactively with
the following command

    cd <directory-repository>
    source tools/env.sh
    python ${MDBN_ROOT}/src/main.py -t OV -c <config-file>.json -l -v

where `<config-file>.json` is the JSON configuration file. Many configuration file examples
are available in the subdirectory `config`.

The sequence above will start analysis of TCGA Ovarian cancer data and it will log
the results under the directory `${MDBN_ROOT}/MDBN_run/OV_Batch_<uuid>` where `<uuid>` is an
unique identifier associated with the configuration file.

The full set of command options is documented below

    --help usage summary
    --tcga=[OV|AML] define the TCGA Project. The default is OV
    --config=filename configuration file
    --daemon listen for a JSON config
    --port=port change the default listening port. The default port is 5000
    --batch=batch_dir load configuration files from a directory
    --s3=bucket store the results on S3 bucket
    --url=url DynamoDB URL. The default is None
    --region=name AWS region name. The default is eu-west-1
    --log=filename output file
    --verbose print additional information during training

##### How to create configuration files from a CSV initialization file

If you have a need to run a batch of experiments with different network architectures
and different hyper-parameters the script `tools/init_configs.sh` will transform a
CSV file into a set of configuration files. An example usage is below

    cd ${MDBN_ROOT}
    mkdir queue
    cd queue
    init_configs.sh ov ../config/ov_configs_2017_02_20_1133_init.csv 

The batch run can now be executed with the command

    python ${MDBN_ROOT}/src/main.py -t OV -b . -l -v
    
