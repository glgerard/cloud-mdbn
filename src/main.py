from __future__ import print_function
import os
import sys
import zipfile
import urllib
import json
import logging
import traceback
import time
import boto3

from MDBN import MDBN
from decimal import Decimal
from flask import Flask
from flask import request
from utils import read_cmdline
from threading import Thread

app = Flask('cloud-mdbn')

# Local DynamoDB instance
dynamodb_url="http://localhost:8000"
region_name='eu-west-1'

BUSY = 10
FREE = 0

class jobDescription():
    def __init__(self):
        self.uuid = ''
        self.status = FREE

    def get_status(self):
        return self.status

    def set_status(self, status, uuid):
        self.uuid = uuid
        self.status = status
        return status

jobStatus = jobDescription()

mdbn = None
project = "OV"

def prepare_TCGA_datafiles(project, config, datadir='data'):
    datafiles = dict()
    for key in config["pathways"]:
        datafiles[key] = config['dbns'][key]["datafile"]

    if project == "AML":
        return datafiles

    base_url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3479191/bin/'
    archive = 'supp_gks725_nar-00961-n-2012-File005.zip'

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

def start_run(uuid, project, config):
    global jobStatus
    jobStatus.set_status(BUSY, uuid)
    datafiles = prepare_TCGA_datafiles(project, config)
    len_classes = mdbn.run(config, datafiles)
    jobStatus.set_status(FREE, uuid)

    timestamp = time.time()
    dynamodb = boto3.resource('dynamodb', region_name=region_name, endpoint_url=dynamodb_url)
    table = dynamodb.Table('jobs')
    for run, len in enumerate(len_classes):
        table.put_item(  # Add the completed job in DynamoDB
            Item={
                'job': uuid,
                'run': run,
                'timestamp': Decimal(timestamp),
                'status': 'DONE',
                'n_classes': len
            }
    )
    return 'job_completed'

@app.route('/status')
def statusCmd():
    global jobStatus
    return 'ready' if jobStatus.get_status() == FREE else 'busy'

@app.route('/run/<uuid>', methods=['POST'])
def runCmd(uuid):
    global jobStatus
    if jobStatus.get_status() == FREE:
        config = request.json
        try:
            thread = Thread(target=start_run, args=(uuid, project, config))
            thread.start()
        except:
            logging.error('Unexpected error (%s): %s' % (uuid, sys.exc_info()[0]))
            logging.error('Unexpected error:(%s): %s' % (uuid, sys.exc_info()[1]))
            traceback.format_exc()
        return uuid
    else:
        return uuid, 403

def main(argv, config_filename='ov_config.json'):
    global mdbn
    global project

    project, daemonized, port, config_filename, log_enabled, verbose = \
        read_cmdline(argv, config_filename)

    mdbn = MDBN(project+'_Batch',log_enabled=log_enabled, verbose=verbose)
    if not daemonized:
        with open('%s' % config_filename) as config_file:
            config = json.load(config_file)
            datafiles = prepare_TCGA_datafiles(project,config)
            mdbn.run(config, datafiles)
    else:
        app.run(host='0.0.0.0',port=port, debug=False)

if __name__ == '__main__':
    main(sys.argv[1:])