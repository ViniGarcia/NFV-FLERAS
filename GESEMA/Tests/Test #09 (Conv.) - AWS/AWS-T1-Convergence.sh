#!/bin/bash

python3 5.GeSeMa.py AWS_REQ_7.yaml -gs GREEDY -cp 0.3 -mp 0.05 -g CONVERGENCE -s 1500 -o T1-GreedyConvergence07-AWS-1500-1.csv
python3 5.GeSeMa.py AWS_REQ_7.yaml -gs GREEDY -cp 0.3 -mp 0.05 -g CONVERGENCE -s 1500 -o T1-GreedyConvergence07-AWS-1500-2.csv
python3 5.GeSeMa.py AWS_REQ_7.yaml -cp 0.3 -mp 0.05 -g CONVERGENCE -s 1500 -o T1-RandomConvergence07-AWS-1500-1.csv
python3 5.GeSeMa.py AWS_REQ_7.yaml -cp 0.3 -mp 0.05 -g CONVERGENCE -s 1500 -o T1-RandomConvergence07-AWS-1500-2.csv

python3 5.GeSeMa.py AWS_REQ_9.yaml -gs GREEDY -cp 0.3 -mp 0.05 -g CONVERGENCE -s 1500 -o T1-GreedyConvergence09-AWS-1500-1.csv
python3 5.GeSeMa.py AWS_REQ_9.yaml -gs GREEDY -cp 0.3 -mp 0.05 -g CONVERGENCE -s 1500 -o T1-GreedyConvergence09-AWS-1500-2.csv
python3 5.GeSeMa.py AWS_REQ_9.yaml -cp 0.3 -mp 0.05 -g CONVERGENCE -s 1500 -o T1-RandomConvergence09-AWS-1500-1.csv
python3 5.GeSeMa.py AWS_REQ_9.yaml -cp 0.3 -mp 0.05 -g CONVERGENCE -s 1500 -o T1-RandomConvergence09-AWS-1500-2.csv

python3 5.GeSeMa.py AWS_REQ_11.yaml -gs GREEDY -cp 0.3 -mp 0.05 -g CONVERGENCE -s 1500 -o T1-GreedyConvergence11-AWS-1500-1.csv
python3 5.GeSeMa.py AWS_REQ_11.yaml -gs GREEDY -cp 0.3 -mp 0.05 -g CONVERGENCE -s 1500 -o T1-GreedyConvergence11-AWS-1500-2.csv
python3 5.GeSeMa.py AWS_REQ_11.yaml -cp 0.3 -mp 0.05 -g CONVERGENCE -s 1500 -o T1-RandomConvergence11-AWS-1500-1.csv
python3 5.GeSeMa.py AWS_REQ_11.yaml -cp 0.3 -mp 0.05 -g CONVERGENCE -s 1500 -o T1-RandomConvergence11-AWS-1500-2.csv