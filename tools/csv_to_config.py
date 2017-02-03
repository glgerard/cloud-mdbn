from __future__ import print_function
import sys
import json
import csv
from hashlib import md5

def main(argv):
    configCsvFile = argv[0]
    configJsonFile = argv[1]

    with open(configJsonFile,'r') as jsonfile:
        templateConfig = json.load(jsonfile)

    with open(configCsvFile, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=',')
        for row in csvreader:
            templateConfig["seed"] = row["seed"]
            templateConfig["runs"] = row["runs"]

            for net in templateConfig['dbns'].keys()+['top']:
                lcNet = net.lower()
                if row[lcNet+'.active'] == "False":
                    break
                if net != 'top':
                    netConfig = templateConfig['dbns'][net]
                else:
                    netConfig = templateConfig[net]
                for (key,value) in netConfig.items():
                    colL2 = lcNet + '.' + key.lower()
                    if isinstance(value, list):
                        for i, _ in enumerate(value):
                            colL3 = colL2 + '.' + str(i)
                            value[i] = row[colL3]
                    else:
                        netConfig[key] = row[colL2]
            print(templateConfig)

    return

if __name__ == '__main__':
    main(sys.argv[1:])