# MDBN

A Theano implementation of a Multimodal Deep Belief Network used for clustering
two types of TCGA tumoral genetic data: Ovarian cancer and Acute Myeloid Leukemia (AML).

The network architecture and tuning hyperparameters are configured with a JSON file.

Detailed instructions on how to setup your work enviroment and test the configuration
are contained in the [HOWTO](doc/HOWTO.md) document.

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
    --instant=timestamp in ISO 8601 format
    --s3=bucket store the results on S3 bucket
    --dynamodb store job status on DynamoDB
    --url=url DynamoDB URL. The default is None
    --region=name AWS region name. The default is eu-west-1
    --log create batch.log file
    --verbose print additional information during training

## Basics on configuration file syntax

The configuration below provides an example of a unimodal DBN
configured with two layers. The first one with 400 nodes and
top one with 40 nodes. The first layer trains for 80 epochs and
the second for 800. The learning rates are respecitvely 0.001 and
0.01 . Finally you can choose with persistent vs. simple Contrastive
Divergence with `k`-steps by setting the `persistent` parameter. 
The `datafile` specifies the source of input data to the DBN and
`batchSize` defines the number of samples per batch.

    "DM": {
        "batchSize": 5, 
        "datafile": "TCGA_Data/3.Methylation_0.5.out", 
        "epochs": [ 80, 800 ], 
        "k": 1, 
        "lambdas": [ 0.01, 0.1 ], 
        "layersNodes": [ 400, 40 ], 
        "lr": [ 0.001, 0.01 ],
        "persistent": true
    }

Other parameters of the JSON file global to the entire network are

    "p": 0.5, 
    "pathways": [
        "ME", 
        "GE", 
        "DM"
    ], 
    "runs": 1, 
    "seed": 1234, 
    "name": "ov_config_2_1.json",
    "uuid": "fe6d1f49efe561c80bc6a1ef1b9eca49"

where
 * `p` is the dropout ratio (1.0 means no dropout);
 * `runs` are the number of consecutive executions;
 * `seed` is the inital seed for the random number generator;
 * `pathways` contains the list of active unimodal DBNs;
 * `name` is a mnemonic name associated to the configuration
 * `uuid` is a unique identifier of the configuration file
 
Finally each network must have a top DBN which is always called
`top`. All other unimodal DBNs must be defined inside the
`dbns` list. See the `${MDBN_ROOT}/config/ov_template.json`
for an example configuration.

## How to create configuration files from a CSV initialization file

If you have a need to run a batch of experiments with different network architectures
and different hyper-parameters the script `tools/init_configs.sh` will transform a
CSV file into a set of configuration files. An example usage is below

    cd ${MDBN_ROOT}
    mkdir queue
    cd queue
    init_configs.sh ov ../config/ov_configs_2017_02_20_1133_init.csv 

The batch run can now be executed with the command

    python ${MDBN_ROOT}/src/main.py -t OV -b . -l -v
    
