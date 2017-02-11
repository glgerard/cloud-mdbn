#!/bin/bash

host="taurus"
port=8000

uuid=$1

aws dynamodb query --table-name jobs --key-conditions "{\"job\": { \"AttributeValueList\": [ { \"S\": \"$uuid\"} ], \"ComparisonOperator\": \"EQ\"}}" --endpoint-url http://$host:$port
