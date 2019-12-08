#!bin/bash

python3 TestFramework.py -t -ne 30 30x7.yaml "-g 500 -cp 0.3 -mp 0.05" "-g 1000 -cp 0.3 -mp 0.05" "-g 2000 -cp 0.3 -mp 0.05" "-g 4000 -cp 0.3 -mp 0.05" "-g 8000 -cp 0.3 -mp 0.05"
python3 TestFramework.py -t -ne 30 30x9.yaml "-g 500 -cp 0.3 -mp 0.05" "-g 1000 -cp 0.3 -mp 0.05" "-g 2000 -cp 0.3 -mp 0.05" "-g 4000 -cp 0.3 -mp 0.05" "-g 8000 -cp 0.3 -mp 0.05"
python3 TestFramework.py -t -ne 30 30x11.yaml "-g 500 -cp 0.3 -mp 0.05" "-g 1000 -cp 0.3 -mp 0.05" "-g 2000 -cp 0.3 -mp 0.05" "-g 4000 -cp 0.3 -mp 0.05" "-g 8000 -cp 0.3 -mp 0.05"

