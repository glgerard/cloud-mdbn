from __future__ import print_function

import copy
import csv
import json
import sys
from ast import literal_eval

from utils import write_config

def csvToConfig(configCsvFile, configJsonFile, callback_fn):
    with open(configJsonFile,'r') as jsonfile:
        templateConfig = json.load(jsonfile)

    with open(configCsvFile, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=',')
        for row in csvreader:
            config = copy.deepcopy(templateConfig)

            config['uuid'] = row['uuid']
            config['name'] = row['config_file']
            config["seed"] = literal_eval(row["seed"])
            config["runs"] = literal_eval(row["runs"])
            config["p"] = literal_eval(row["p"])

            pathways=[]

            for net in config['dbns'].keys()+['top']:
                lcNet = net.lower()
                if literal_eval(row[lcNet+'.active']):
                    if net != 'top':
                        pathways.append(net)
                    if net != 'top':
                        netConfig = config['dbns'][net]
                    else:
                        netConfig = config[net]
                    for (key,value) in netConfig.items():
                        colL2 = lcNet + '.' + key.lower()
                        if isinstance(value, list):
                            for i, _ in enumerate(value):
                                colL3 = colL2 + '.' + str(i)
                                value[i] = literal_eval(row[colL3])
                        else:
                            try:
                                netConfig[key] = literal_eval(row[colL2])
                            except:
                                netConfig[key] = row[colL2]

            config['pathways'] = pathways

            callback_fn(config, config['name'])

    return


if __name__ == '__main__':
    if(len(sys.argv)<3):
        print("Usage: %s <config.csv> <config.json>" % sys.argv[0], file=sys.stderr)
        exit(1)
    csvToConfig(sys.argv[1], sys.argv[2], write_config)