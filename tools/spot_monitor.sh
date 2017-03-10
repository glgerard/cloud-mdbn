#!/usr/bin/env bash

URL=http://169.254.169.254/latest/meta-data/spot/termination-time
while [[ `if curl -s $URL | grep -q .*T.*Z; then echo terminated; fi` != "terminated" ]]; do
    sleep 5
done

echo "Handling termination"

aws s3 cp payload.zip s3://${s3bucket}/payload
