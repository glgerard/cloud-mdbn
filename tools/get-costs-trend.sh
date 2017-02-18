#!/bin/bash
# Scan the batch.log files and extract from each the cost trends

RUN_DIR=${MDBN_ROOT}/MDBN_run
OUT_DIR=${MDBN_ROOT}/results
PREFIX=OV
BATCHLOG=batch.log

cat ${OUT_DIR}/${PREFIX}_costs_header.csv > ${OUT_DIR}/${PREFIX}_costs_trend.csv

for dir in ${RUN_DIR}/${PREFIX}*; do
    echo $dir
    uuid=$(grep CONFIG_UUID ${dir}/${BATCHLOG} | cut -d':' -f2)
    grep epoch ${dir}/${BATCHLOG} | cut -d':' -f 2,4,6,8,10 --output-delimiter=',' | sed -e "s/^/${uuid},/g" >> ${OUT_DIR}/${PREFIX}_costs_trend.csv
done

#cat ${OUT_DIR}/${PREFIX}_classes_header.csv > ${OUT_DIR}/${PREFIX}_classes.csv

find ${RUN_DIR} -name batch.log -exec egrep 'UUID|classes' {} \; > /tmp/batch.tmp
awk < /tmp/batch.tmp '
BEGIN  { FS=":"; print "uuid,run,n_classes" }
/UUID/ { uuid=$2 }
/classes/ { print uuid "," $2 "," $4 }
' > ${OUT_DIR}/${PREFIX}_classes.csv
