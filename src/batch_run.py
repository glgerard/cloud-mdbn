from __future__ import print_function
import requests
import sys
from time import sleep
from hashlib import md5
import logging
import traceback
from csv_to_config import csvToConfig

host = '127.0.0.1'
port = 5000

jobCompleted = False

def main(configCsvFile, configJsonFile):
    try:
        csvToConfig(configCsvFile, configJsonFile, send_config)
    except Exception:
        print(traceback.format_exc())

def check_completion():
    jobRunning = True
    while jobRunning:
        sleep(30)
        r = requests.get('http://%s:%d/status' % (host, port))
        if r.status_code == requests.codes.ok:
            jobRunning = r.text == 'busy'
        else:
            r.raise_for_status()
    return

def send_config(config, configFile = None):
    try:
        r = requests.get('http://%s:%d/status' % (host, port))
        if r.status_code == requests.codes.ok:
            if r.text == 'ready':
                print(configFile)
                uuid = md5(str(config.values())).hexdigest()
                r = requests.post('http://%s:%d/run/%s' % (host, port, uuid),
                                  json=config)
                if r.status_code == requests.codes.ok:
                    check_completion()
                else:
                    r.raise_for_status()
        else:
            r.raise_for_status()
    except Exception as e:
        print(e)
        traceback.format_exc()

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
