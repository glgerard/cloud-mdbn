import os
import sys
import zipfile
import urllib
import json
import logging
import traceback
from threading import Thread

from flask import Flask
from flask import request

app = Flask('cloud-mdbn')

import MDBN

batch_output_dir = ''
batch_start_date_str = ''

BUSY = 10
FREE = 0

class jobDescription():
    def __init__(self):
        self.uuid = ''
        self.status = FREE
        self.min = 0
        self.median = 0
        self.max = 0

    def get_status(self):
        return self.status

    def set_status(self, status, uuid, minimum=0, median=0, maximum=0):
        self.uuid = uuid
        self.status = status
        self.min = minimum
        self.median = median
        self.max = maximum
        return status

jobStatus = jobDescription()

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

def start_run(uuid, config, verbose):
    global jobStatus
    jobStatus.set_status(BUSY, uuid)
    datafiles = prepare_OV_TCGA_datafiles(config)
    minimum, median, maximum = MDBN.run(config, datafiles, verbose)
    jobStatus.set_status(FREE, uuid, minimum, median, maximum)
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
            thread = Thread(target=start_run, args=(uuid, config, verbose))
            thread.start()
        except:
            logging.error('Unexpected error (%s): %s' % (uuid, sys.exc_info()[0]))
            logging.error('Unexpected error:(%s): %s' % (uuid, sys.exc_info()[1]))
            traceback.format_exc()
        return uuid, 202
    else:
        return uuid, 403

@app.route('/median/<uuid>')
def getMedian(uuid):
    global jobStatus
    if jobStatus.uuid == uuid and jobStatus.status == FREE:
        return "%s" % jobStatus.median
    else:
        return "NA", 404

@app.route('/min/<uuid>')
def getMin(uuid):
    global jobStatus
    if jobStatus.uuid == uuid and jobStatus.status == FREE:
        return "%s" % jobStatus.min
    else:
        return "NA", 404

@app.route('/max/<uuid>')
def getMax(uuid):
    global jobStatus
    if jobStatus.uuid == uuid and jobStatus.status == FREE:
        return "%s" % jobStatus.max
    else:
        return "NA", 404

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
        app.run(port=port, debug=False)

if __name__ == '__main__':
    main(sys.argv[1:])