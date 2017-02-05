import os
import sys
import zipfile
import urllib
import json
import requests

from flask import Flask
from flask import request

app = Flask('cloud-mdbn')

import MDBN

batch_output_dir = ''
batch_start_date_str = ''
BUSY = 10
FREE = 0
netStatus = FREE
verbose = False

def prepare_OV_TCGA_datafiles(config, datadir='data'):
    base_url = 'http://nar.oxfordjournals.org/content/suppl/2012/07/25/gks725.DC1/'
    archive = 'nar-00961-n-2012-File005.zip'

    datafiles = dict()
    for key in config["pathways"]:
        datafiles[key] = config['dbns'][key]["datafile"]

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

def get_status():
    return netStatus

def set_status(s):
    global netStatus
    netStatus = s
    return netStatus

@app.route('/status')
def statusCmd():
    return 'ready' if get_status() == FREE else 'busy'

@app.route('/run/<uuid>', methods=['POST'])
def runCmd(uuid):
    if get_status() == FREE:
        config = request.json
        print(config)
        set_status(BUSY)
        print(get_status())
        datafiles = prepare_OV_TCGA_datafiles(config)
        MDBN.run(config, datafiles, verbose)
        set_status(FREE)
    return uuid

def main(argv, batch_dir_prefix='OV_Batch', config_filename='ov_config.json'):
    daemonized, port, config_filename, verbose = \
        MDBN.init(argv, batch_dir_prefix, config_filename)

    print (batch_output_dir)
    if not daemonized:
        with open('%s' % config_filename) as config_file:
            config = json.load(config_file)
            datafiles = prepare_OV_TCGA_datafiles(config)
            MDBN.run(config, datafiles, verbose)
    else:
        app.run(port=port, debug=False, threaded= True)

if __name__ == '__main__':
    main(sys.argv[1:])