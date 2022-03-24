#!/bin/bash

python3 5.GeSeMa.py AWS_REQ_11_NO_DU.yaml -tt 10 -cp 0.3 -mp 0.05 -o RESULT_AWS_11_NO_DU.csv
python3 5.GeSeMa.py AWS_REQ_11_NO_GD.yaml -tt 10 -cp 0.3 -mp 0.05 -o RESULT_AWS_11_NO_GD.csv
python3 5.GeSeMa.py AWS_REQ_11.yaml -tt 10 -cp 0.3 -mp 0.05 -o RESULT_AWS_11.csv