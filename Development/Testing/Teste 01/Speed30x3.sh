#!/bin/bash
echo "P20"
python3 TestFramework.py -t -e 30 30x3.yaml "-p 20 -g 500" "-p 20 -g 1000" "-p 20 -g 1500" "-p 20 -g 2000" "-p 20 -g 2500"
mv 30x3TIMING.csv 30x3TIMING-P20.csv
echo "P40"
python3 TestFramework.py -t -ne 30 30x3.yaml "-p 40 -g 500" "-p 40 -g 1000" "-p 20 -g 1500" "-p 40 -g 2000" "-p 40 -g 2500"
mv 30x3TIMING.csv 30x3TIMING-P40.csv
echo "P60"
python3 TestFramework.py -t -ne 30 30x3.yaml "-p 60 -g 500" "-p 60 -g 1000" "-p 60 -g 1500" "-p 60 -g 2000" "-p 60 -g 2500"
mv 30x3TIMING.csv 30x3TIMING-P60.csv
echo "P80"
python3 TestFramework.py -t -ne 30 30x3.yaml "-p 80 -g 500" "-p 80 -g 1000" "-p 80 -g 1500" "-p 80 -g 2000" "-p 80 -g 2500"
mv 30x3TIMING.csv 30x3TIMING-P80.csv
echo "P100"
python3 TestFramework.py -t -ne 30 30x3.yaml "-p 100 -g 500" "-p 100 -g 1000" "-p 100 -g 1500" "-p 100 -g 2000" "-p 100 -g 2500"
mv 30x3TIMING.csv 30x3TIMING-P100.csv