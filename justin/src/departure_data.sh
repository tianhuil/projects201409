#!/bin/bash
for f in /Users/jcb/Documents/Data-Incubator/taxi-project/data/dayhour/*.csv.gz
do
	echo "Processing $f..."
	gzcat $f | python mr_num_departures.py > ${f%.csv.gz}.txt
done

