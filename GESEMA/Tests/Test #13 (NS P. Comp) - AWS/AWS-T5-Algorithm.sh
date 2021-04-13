#!/bin/bash

python3 TestFramework.py -rq -g "-gs GREEDY -g 20000 -cp 0.3 -mp 0.05" "-g 20000 -cp 0.3 -mp 0.05" "-a NSGA2 -gs GREEDY -g 20000 -cp 0.3 -mp 0.05" "-a NSGA2 -g 20000 -cp 0.3 -mp 0.05"  -r 30 -f AWS_REQ_7.yaml
python3 TestFramework.py -rq -g "-gs GREEDY -g 20000 -cp 0.3 -mp 0.05" "-g 20000 -cp 0.3 -mp 0.05" "-a NSGA2 -gs GREEDY -g 20000 -cp 0.3 -mp 0.05" "-a NSGA2 -g 20000 -cp 0.3 -mp 0.05" -r 30 -f AWS_REQ_9.yaml
python3 TestFramework.py -rq -g "-gs GREEDY -g 20000 -cp 0.3 -mp 0.05" "-g 20000 -cp 0.3 -mp 0.05" "-a NSGA2 -gs GREEDY -g 20000 -cp 0.3 -mp 0.05" "-a NSGA2 -g 20000 -cp 0.3 -mp 0.05" -r 30 -f AWS_REQ_11.yaml
