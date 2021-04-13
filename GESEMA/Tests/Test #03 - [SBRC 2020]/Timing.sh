#!bin/bash

python3 TestFramework.py -t -g "-g 500 -cp 0.3 -mp 0.05" "-g 1000 -cp 0.3 -mp 0.05" "-g 2000 -cp 0.3 -mp 0.05" "-g 4000 -cp 0.3 -mp 0.05" "-g 8000 -cp 0.3 -mp 0.05" -r 30 -f 30x7.yaml
python3 TestFramework.py -t -g "-g 500 -cp 0.3 -mp 0.05" "-g 1000 -cp 0.3 -mp 0.05" "-g 2000 -cp 0.3 -mp 0.05" "-g 4000 -cp 0.3 -mp 0.05" "-g 8000 -cp 0.3 -mp 0.05" -r 30 -f 30x9.yaml
python3 TestFramework.py -t -g "-g 500 -cp 0.3 -mp 0.05" "-g 1000 -cp 0.3 -mp 0.05" "-g 2000 -cp 0.3 -mp 0.05" "-g 4000 -cp 0.3 -mp 0.05" "-g 8000 -cp 0.3 -mp 0.05" -r 30 -f 30x11.yaml

