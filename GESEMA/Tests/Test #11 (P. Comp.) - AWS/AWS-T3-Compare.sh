#!/bin/bash

python3 TestFramework.py -rq -ra "-r 100000" -g "-g 2000 -cp 0.3 -mp 0.05" -sg "-sk 2 -r 50000" "-sk 4 -r 25000" -r 30 -f AWS_REQ_7.yaml
python3 TestFramework.py -rq -ra "-r 100000" -g "-g 2000 -cp 0.3 -mp 0.05" -sg "-sk 2 -r 50000" "-sk 4 -r 25000" -r 30 -f AWS_REQ_9.yaml
python3 TestFramework.py -rq -ra "-r 100000" -g "-g 2000 -cp 0.3 -mp 0.05" -sg "-sk 2 -r 50000" "-sk 4 -r 25000" -r 30 -f AWS_REQ_11.yaml
