import os
import sys
import zipfile
import urllib

from MDBN import run_mdbn
from utils import init

def prepare_OV_TCGA_datafiles(config, datadir='data'):
    base_url = 'http://nar.oxfordjournals.org/content/suppl/2012/07/25/gks725.DC1/'
    archive = 'nar-00961-n-2012-File005.zip'

    datafiles = dict()
    for key in config["pathways"]:
        datafiles[key] = config[key]["datafile"]

    if not os.path.isdir(datadir):
        os.mkdir(datadir)

    root_dir = os.getcwd()
    os.chdir(datadir)
    for name, datafile in datafiles.iteritems():
        if not os.path.isfile(datafile):
            if not os.path.isfile(archive):
                print('Downloading TCGA_Data from ' + base_url)
                testfile = urllib.URLopener()
                testfile.retrieve(base_url + archive, archive)
            zipfile.ZipFile(archive, 'r').extract(datafile)
    os.chdir(root_dir)
    return datafiles

def main(argv, batch_dir_prefix='OV_Batch', config_filename='ov_config.json'):
    batch_output_dir, batch_start_date_str, config, numpy_rng, verbose = \
        init(argv, batch_dir_prefix, config_filename)

    datafiles = prepare_OV_TCGA_datafiles(config)

    results = []

    run_mdbn(batch_output_dir, batch_start_date_str, config, datafiles, numpy_rng, results, verbose)

if __name__ == '__main__':
    main(sys.argv[1:])