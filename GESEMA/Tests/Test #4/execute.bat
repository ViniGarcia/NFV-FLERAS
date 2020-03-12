FOR /L %%A IN (1,1,50) DO (
ECHO %%A 
ECHO "(0)"
python Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 0 -o output_df_0.csv
python Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 0 -fm 0.5 -o output_fm_0.csv

ECHO "(1)"
python Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 1 -o output_df_1.csv
python Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 1 -fm 0.5 -o output_fm_1.csv

ECHO "(2)"
python Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 2 -o output_df_2.csv
python Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 2 -fm 0.5 -o output_fm_2.csv

ECHO "(3)"
python Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 3 -o output_df_3.csv
python Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 3 -fm 0.5 -o output_fm_3.csv

ECHO "(4)"
python Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 4 -o output_df_4.csv
python Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 4 -fm 0.5 -o output_fm_4.csv

ECHO "(5)"
python Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 5 -o output_df_5.csv
python Online-GeSeMa.py 30x13.yaml -g 5000 -s 2500 -pu 5 -fm 0.5 -o output_fm_5.csv

python check.py
)

python process.py
