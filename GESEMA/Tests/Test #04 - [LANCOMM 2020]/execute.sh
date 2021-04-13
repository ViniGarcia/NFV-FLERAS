#!/bin/bash

for i in `seq 1 50`; do
echo $i
echo "(0)"
python3 Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 0 -o output_df_0.csv
python3 Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 0 -fm 0.5 -o output_fm_0.csv

echo "(1)"
python3 Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 1 -o output_df_1.csv
python3 Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 1 -fm 0.5 -o output_fm_1.csv

echo "(2)"
python3 Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 2 -o output_df_2.csv
python3 Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 2 -fm 0.5 -o output_fm_2.csv

echo "(3)"
python3 Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 3 -o output_df_3.csv
python3 Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 3 -fm 0.5 -o output_fm_3.csv

echo "(4)"
python3 Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 4 -o output_df_4.csv
python3 Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 4 -fm 0.5 -o output_fm_4.csv

echo "(5)"
python3 Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 5 -o output_df_5.csv
python3 Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 5 -fm 0.5 -o output_fm_5.csv

python3 check.py
done

python3 process.py
