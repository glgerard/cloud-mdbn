from __future__ import print_function
import requests
import sys
from time import sleep
from hashlib import md5
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import time
import logging
import traceback
from csv_to_config import csvToConfig

host = '127.0.0.1'
port = 5000

# Local DynamoDB instance
dynamodb_url="http://localhost:8000"
region_name='eu-west-1'

jobCompleted = False

def main(configCsvFile, configJsonFile):
    global table

    client = boto3.client('dynamodb', region_name=region_name, endpoint_url=dynamodb_url)
    list_tables = client.list_tables()
    dynamodb = boto3.resource('dynamodb', region_name=region_name, endpoint_url=dynamodb_url)
    if not 'jobs' in list_tables['TableNames']:
        table = dynamodb.create_table(
            TableName='jobs',
            KeySchema=[
                {
                    'AttributeName': 'job',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'n_classes',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'job',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'n_classes',
                    'AttributeType': 'N'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName='jobs')
    else:
        table = dynamodb.Table('jobs')

    try:
        csvToConfig(configCsvFile, configJsonFile, send_config)
    except Exception:
        print(traceback.format_exc())

def wait_job():
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
    uuid = md5(str(config.values())).hexdigest()

    response = table.query(
        KeyConditionExpression=Key('job').eq(uuid)
    )

    done=False
    for i in response['Items']:
        done=True
        print('Run with UUID %s already completed with %s classes' % (uuid, i['n_classes']))
        print('Date: ' + datetime.fromtimestamp(i['timestamp']).strftime("%Y-%m-%d_%H%M"))

    if done:
        return

    try:
        timestamp = time.time()

        r = requests.get('http://%s:%d/status' % (host, port))
        if r.status_code == requests.codes.ok:
            if r.text == 'ready':
                print('JOB UUID: ' + uuid)
                r = requests.post('http://%s:%d/run/%s' % (host, port, uuid),
                                  json=config)
                if r.status_code == requests.codes.ok:
                    wait_job()
                    r = requests.get('http://%s:%d/median/%s' % (host, port, uuid))
                    if r.status_code == requests.codes.ok:
                        n_classes = int(r.text)
                        table.put_item(  # Add the completed job in DynamoDB
                            Item={
                                'job': uuid,
                                'n_classes': n_classes,
                                'timestamp': timestamp
                            }
                        )
                    else:
                        r.raise_for_status()
                else:
                    r.raise_for_status()
        else:
            r.raise_for_status()
    except:
        logging.error('Unexpected error (%s): %s' % (uuid, sys.exc_info()[0]))
        logging.error('Unexpected error (%s): %s' % (uuid, sys.exc_info()[1]))
        traceback.format_exc()

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
