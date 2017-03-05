from __future__ import print_function
import os
import sys
import zipfile
import requests
import StringIO
import json
import logging
import traceback
import time
import boto3
import glob

from MDBN import MDBN
from decimal import Decimal
from flask import Flask
from flask import request
from utils import read_cmdline
from utils import get_dyndb_table
from utils import run_completed
from threading import Thread

app = Flask('cloud-mdbn')

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

def prepare_TCGA_datafiles(project, config, datadir='data'):
    datafiles = dict()
    for key in config["pathways"]:
        datafiles[key] = config['dbns'][key]["datafile"]

    if project == "AML":
        return datafiles

    base_url = 'http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3479191/bin/'
    archive = 'supp_gks725_nar-00961-n-2012-File005.zip'

    if not os.path.isdir(datadir):
        os.mkdir(datadir)

    root_dir = os.getcwd()
    os.chdir(datadir)
    for name, datafile in datafiles.iteritems():
        if not os.path.isfile(datafile):
            if not os.path.isfile(archive):
                print('Downloading TCGA_Data from ' + base_url)
                try:
#                    testfile = urllib.URLopener()
#                    testfile.retrieve(base_url + archive, archive)
                    r = requests.get(base_url + archive, stream=True)
                    if r.status_code == requests.codes.ok:
                        zipfile.ZipFile(
                            StringIO.StringIO(r.content)).extractall()
                    else:
                        r.raise_for_status()
                except:
                    print("Error ({0}): {1}".format(sys.exc_info()[0], sys.exc_info()[1]))
                    sys.exit(-1)
    os.chdir(root_dir)
    return datafiles

def start_run(config):
    global jobStatus
    uuid = config['uuid']

    if run_completed(dyndb_table, uuid):
        return 'job_completed'

    jobStatus.set_status(BUSY, uuid)
    datafiles = prepare_TCGA_datafiles(project, config)
    len_classes = mdbn.run(config, datafiles)
    jobStatus.set_status(FREE, uuid)

    timestamp = time.time()
    for run, len in enumerate(len_classes):
        len = int(len)
        if dyndb_table is not None:
            dyndb_table.put_item(  # Add the completed job in DynamoDB
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
    if jobStatus.get_status() == FREE:
        config = request.json
        if uuid == config['uuid']:
            try:
                thread = Thread(target=start_run, args=(config))
                thread.start()
            except:
                logging.error('Unexpected error (%s): %s' % (uuid, sys.exc_info()[0]))
                logging.error('Unexpected error:(%s): %s' % (uuid, sys.exc_info()[1]))
                traceback.format_exc()
            return uuid
        else:
            return uuid, 400
    else:
        return uuid, 403

def main(argv, config_filename='ov_config.json'):
    global mdbn
    global project
    global s3_bucket
    global dyndb_table

    project, daemon, port, batch_dir, \
    config_filename, s3_bucket_name, \
    dynamodb, dynamodb_url, region_name, \
    log_enabled, verbose = \
        read_cmdline(argv, config_filename)

    if dynamodb:
        dyndb_table = get_dyndb_table(dynamodb_url, region_name)
    else:
        dyndb_table = None

    if s3_bucket_name is not None:
        s3 = boto3.resource('s3')
        s3_bucket = s3.Bucket(s3_bucket_name)
    else:
        s3_bucket = None

    mdbn = MDBN(project+'_Batch',log_enabled=log_enabled, verbose=verbose,
                s3_bucket=s3_bucket)

    if not daemon:
        if batch_dir is None:
            runConfig(config_filename)
        else:
            config_files = glob.glob('%s/%s*.json' %
                                     (batch_dir, project.lower()))
            for config_filename in config_files:
                runConfig(config_filename)
    else:
        app.run(host='0.0.0.0',port=port, debug=False)

def runConfig(config_filename):
    try:
        config_file = open('%s' % config_filename)
        config = json.load(config_file)
        start_run(config)
    except IOError as e:
        print("Could not open %s " % config_filename)
        print("I/O error ({0}): {1}".format(e.errno, e.strerror))

if __name__ == '__main__':
    main(sys.argv[1:])