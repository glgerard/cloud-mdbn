from __future__ import print_function
import sys
import json
import csv
import copy
from ast import literal_eval

def main(argv):
    configCsvFile = argv[0]
    configJsonFile = argv[1]

    with open(configJsonFile,'r') as jsonfile:
        templateConfig = json.load(jsonfile)


    with open(configCsvFile, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=',')
        for row in csvreader:
            print(row)

            config = copy.deepcopy(templateConfig)

            config["seed"] = literal_eval(row["seed"])
            config["runs"] = literal_eval(row["runs"])

            pathways=[]

            for net in config['dbns'].keys()+['top']:
                lcNet = net.lower()
                print(literal_eval(row[lcNet+'.active']))
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
            with open(row['config_file'], 'w') as f:
                json.dump(config, f, indent=4, sort_keys=True)

    return

if __name__ == '__main__':
    main(sys.argv[1:])