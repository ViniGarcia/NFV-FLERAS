#!/bin/bash

executeGeSeMa(){
	exec=30
	
	file="../$1/Mod_$2/heritage_$6/$1-modified.yaml"
	heritage="../$1/heritage_base/$6/heritage-$1-g_$3-p_$4-h_30-$5%.csv"
	target="../$1/h4/heritage_$6/$1-Mod_$2-RELQUALITY(g_$3-p_$4-h_30-$6-$5%).csv"
	
	python3 TestFramework.py -rq -g "-g $3 -p $4" "-g $3 -p $4 -i $heritage" -r $exec -f $file

	cp -v RELQUALITY.csv $target
	rm -vf RELQUALITY.csv
}

case="35x11"

g=30000
p=100

mods=3

mod=11
for (( i=0; i<$mods; i++ ))
do
	h=50
	executeGeSeMa $case $mod $g $p $h 'random'
	executeGeSeMa $case $mod $g $p $h 'bests'

	h=100
	executeGeSeMa $case $mod $g $p $h 'random'
	executeGeSeMa $case $mod $g $p $h 'bests'
	
	((mod+=1))
done

