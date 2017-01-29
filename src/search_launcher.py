import sys
import csv
import json
import copy
import requests
from hashlib import md5

def usage():
    print "exp_launcher <experiment.csv> <template.json>"

def main(argv):
    host = '127.0.0.1'
    port = 5000

    experimentCsvFile = argv[0]
    templateJsonFile = argv[1]

    with open(templateJsonFile,'r') as jsonfile:
        templateConfig = json.load(jsonfile)

    print(templateConfig)

    experimentParams = dict()
    with open(experimentCsvFile, 'r') as csvfile:
        # Skip header
        csvfile.readline()
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            dbn = row[0]
            layer = int(row[1])
            param = row[2]
            n = int(row[4])
            valuesList = row[5:5+n]

            if not dbn in experimentParams:
                experimentParams[dbn] = dict()

            if not 'layers' in experimentParams[dbn]:
                experimentParams[dbn]['layers'] = []

            if layer == -1:
                experimentParams[dbn][param] = valuesList
            else:
                experimentParams[dbn]['layers'].append(layer)
                if not layer in experimentParams[dbn]:
                    experimentParams[dbn][layer] = dict()

                experimentParams[dbn][layer][param] = valuesList

    print(experimentParams)

    # Search the space of hyperparameters for all the unimodal DBNs
    count=0
    for dbn in templateConfig['pathways']:
        newConfig = copy.deepcopy(templateConfig)
        for key in templateConfig['dbns']:
            if key != dbn:
                newConfig['dbns'].pop(key, None)
        newConfig['pathways'] = [dbn]
        for k in experimentParams[dbn]['k']:
            newConfig['dbns']['k'] = int(k)
            for layer in experimentParams[dbn]['layers']:
                for epoch in experimentParams[dbn][layer]['epochs']:
                    for lr in experimentParams[dbn][layer]['lr']:
                        print ('>>> %d' % count)
                        newConfig['dbns'][dbn]['epochs'][layer] = int(epoch)
                        newConfig['dbns'][dbn]['lr'][layer] = float(lr)
                        print(newConfig)
                        uuid = md5(str(newConfig)).hexdigest()
                        r = requests.post('http://%s:%d/api/run_net/%s' % (host, port, uuid),
                                          json=newConfig)
                        count=count+1
                        sys.exit()

    return

if __name__ == '__main__':
    main(sys.argv[1:])