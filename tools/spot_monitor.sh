#!/usr/bin/env bash

URL=http://169.254.169.254/latest/meta-data/spot/termination-time

function monitor {
    if curl -s $URL | grep -q .*T.*Z; then echo terminated; fi
}

while [[ monitor != "terminated" ]]; do
    sleep 5

    if [ -z `pgrep -u ubuntu python` ]; then
        shutdown
    fi
done

echo "Handling termination"

pkill -u ubuntu python

zip -r9 payload.zip payload

aws s3 cp payload.zip s3://${s3bucket}/payload

