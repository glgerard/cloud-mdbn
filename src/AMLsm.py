import sys

from utils import init
from MDBN import run

def prepare_AML_TCGA_datafiles(config):

    datafiles = dict()
    for key in config["pathways"]:
        datafiles[key] = config[key]["datafile"]

    return datafiles

def main(argv, batch_dir_prefix = 'AML_Batch_', config_filename = 'aml_config.json'):
    batch_output_dir, batch_start_date_str, config, numpy_rng, verbose = \
        init(argv, batch_dir_prefix, config_filename)

    datafiles = prepare_AML_TCGA_datafiles(config)

    run(batch_output_dir, batch_start_date_str, config, datafiles, numpy_rng, results, verbose)

if __name__ == '__main__':
    main(sys.argv[1:])