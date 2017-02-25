#!/usr/bin/env bash

host="taurus"
port=8000

uuid=$1
run=$2
n_classes=$3

CMD="aws dynamodb update-item --table-name"

TABLE="jobs"

$CMD $TABLE --key "{\"job\": {\"S\": \"$uuid\"}, \"run\": {\"N\": \"$run\"}}" \
--update-expression "SET #N = :n" \
--expression-attribute-names '{ "#N":"n_classes" }' \
--expression-attribute-values "{\":n\": {\"N\": \"$n_classes\"}}" \
--return-values ALL_NEW --endpoint-url http://$host:$port
