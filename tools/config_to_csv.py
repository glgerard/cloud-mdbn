from __future__ import print_function
import sys
import json

def main(argv):
    configJsonFile = argv[0]

    with open(configJsonFile,'r') as jsonfile:
        config = json.load(jsonfile)

    print(configJsonFile, end=',')
    print(config["seed"],end=',')
    print(config["runs"],end=',')
    print(config["p"],end=',')

    for net in config['dbns'].keys()+['top']:
        if net != 'top':
            netConfig = config['dbns'][net]
            active = net in config['pathways']
        else:
            active = True
            netConfig = config['top']
        print(active, end=',')
        for (key,value) in netConfig.items():
            if isinstance(value, list):
                for v in value:
                    if active:
                        print("%s" % v, end=',')
                    else:
                        print("NA", end=',')
            else:
                if active:
                    print("%s" % value, end=',')
                else:
                    print("NA", end=',')

    config_hash = config['uuid']
    print(config_hash)

    return

if __name__ == '__main__':
    main(sys.argv[1:])