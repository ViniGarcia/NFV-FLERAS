#!/bin/bash

python3 TestFramework.py -rq -ra "-t 10" -g "-tt 10 -cp 0.3 -mp 0.05" -sg "-sk 2 -t 10" "-sk 4 -t 10" -r 30 -f AWS_REQ_7.yaml
python3 TestFramework.py -rq -ra "-t 10" -g "-tt 10 -cp 0.3 -mp 0.05" -sg "-sk 2 -t 10" "-sk 4 -t 10" -r 30 -f AWS_REQ_9.yaml
python3 TestFramework.py -rq -ra "-t 10" -g "-tt 10 -cp 0.3 -mp 0.05" -sg "-sk 2 -t 10" "-sk 4 -t 10" -r 30 -f AWS_REQ_11.yaml
