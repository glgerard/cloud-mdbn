import requests
import sys
from csv_to_config import csvToConfig

host = '127.0.0.1'
port = 5000
ip = '127.0.0.1'

from flask import Flask
from flask import request

app = Flask('cloud-mdbn')

@app('/')
def statusCmd():
    return

def main(argv):
    csvToConfig(argv[0], argv[1], send_config)

def send_config(config, configFile = None):
    r = requests.post('http://%s:%d/run/%s' % (host, port, ip), json=config)
    while status==BUSY:
        sleep(30)

if __name__ == '__main__':
    app.run(port=port, debug=False, threaded=True)
    main(sys.argv[1:])