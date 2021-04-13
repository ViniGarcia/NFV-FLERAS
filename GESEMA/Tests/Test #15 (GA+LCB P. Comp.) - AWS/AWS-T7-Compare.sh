#!/bin/bash

python3 TestFramework.py -rq -gl "-on BJS_10 -dn SEA19 -kp 25 -ni 50 -ng 20000 -nc 20001 -mp 0.05" -g "-gs GREEDY -g 20000 -cp 0.5 -mp 0.05" "-g 20000 -cp 0.5 -mp 0.05" -r 30 -f AWS_REQ_7_GALCB.yaml
python3 TestFramework.py -rq -gl "-on BJS_10 -dn SEA19 -kp 25 -ni 50 -ng 20000 -nc 20001 -mp 0.05" -g "-gs GREEDY -g 20000 -cp 0.5 -mp 0.05" "-g 20000 -cp 0.5 -mp 0.05" -r 30 -f AWS_REQ_9_GALCB.yaml
python3 TestFramework.py -rq -gl "-on BJS_10 -dn SEA19 -kp 25 -ni 50 -ng 20000 -nc 20001 -mp 0.05" -g "-gs GREEDY -g 20000 -cp 0.5 -mp 0.05" "-g 20000 -cp 0.5 -mp 0.05" -r 30 -f AWS_REQ_11_GALCB.yaml