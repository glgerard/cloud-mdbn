from __future__ import print_function

import logging
import sys
import traceback
from datetime import datetime
from time import sleep

import requests
from utils import run_completed

from csv_to_config import csvToConfig
from utils import get_dyndb_table

host = 'taurus'
port = 5000

# Local DynamoDB instance
dynamodb_url="http://taurus:8000"
region_name='eu-west-1'

jobCompleted = False

def main(configCsvFile, configJsonFile):
    global dyndb_table
    dyndb_table = get_dyndb_table(dynamodb_url, region_name)

    try:
        csvToConfig(configCsvFile, configJsonFile, send_config)
    except Exception:
        print(traceback.format_exc())

def wait_job():
    jobRunning = True
    while jobRunning:
        sleep(60)
        r = requests.get('http://%s:%d/status' % (host, port))
        if r.status_code == requests.codes.ok:
            print("[%s]: %s" % (datetime.now(), r.text))
            jobRunning = r.text == 'busy'
        else:
            r.raise_for_status()
    return

def send_config(config, configFile = None):
#    uuid = md5(str(config.values())).hexdigest()
    uuid = config['uuid']

    if run_completed(dyndb_table, uuid):
        return

    try:
        r = requests.get('http://%s:%d/status' % (host, port))
        if r.status_code == requests.codes.ok:
            if r.text == 'ready':
                print('[%s]: Launching job with uuid %s' % (datetime.now(),uuid))
                r = requests.post('http://%s:%d/run/%s' % (host, port, uuid),
                                  json=config)
                if r.status_code == requests.codes.ok:
                    wait_job()
                    print('[%s]: Job with uuid %s completed' % (datetime.now(),uuid))
                else:
                    r.raise_for_status()
        else:
            r.raise_for_status()
    except:
        logging.error('Unexpected error (%s): %s' % (uuid, sys.exc_info()[0]))
        logging.error('Unexpected error (%s): %s' % (uuid, sys.exc_info()[1]))
        traceback.format_exc()

if __name__ == '__main__':
    if(len(sys.argv)<3):
        print("Usage: %s <config.csv> <config.json>" % sys.argv[0], file=sys.stderr)
        exit(1)
    main(sys.argv[1], sys.argv[2])
