from __future__ import print_function
import sys
import json
import csv
import copy
from ast import literal_eval

def csvToConfig(configCsvFile, configJsonFile, callback_fn):
    with open(configJsonFile,'r') as jsonfile:
        templateConfig = json.load(jsonfile)


    with open(configCsvFile, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=',')
        for row in csvreader:
            config = copy.deepcopy(templateConfig)

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
            config['uuid'] = row['uuid']
            callback_fn(config, row['config_file'])

    return

def write_config(config, configFile):
    with open(configFile, 'w') as f:
        json.dump(config, f, indent=4, sort_keys=True)

if __name__ == '__main__':
    csvToConfig(sys.argv[1], sys.argv[2], write_config)