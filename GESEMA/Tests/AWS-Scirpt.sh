!/bin/bash

cp 2.Requests/AWS_REQ_7.yaml ./
cp 2.Requests/AWS_REQ_9.yaml ./
cp 2.Requests/AWS_REQ_11.yaml ./

cp 2.Requests/AWS_REQ_7_GALCB.yaml ./
cp 2.Requests/AWS_REQ_9_GALCB.yaml ./
cp 2.Requests/AWS_REQ_11_GALCB.yaml ./

cp 1.Algorithms/* ./
cp 3.Resources/TestFramework.py ./

echo "T#09 - GeSeMa Convergence Test"
cp Test\ #09\ \(Conv.\)\ -\ AWS/AWS-T1-Convergence.sh ./
chmod +x AWS-T1-Convergence.sh
./AWS-T1-Convergence.sh
mv T1-GreedyConvergence07-AWS-1500-1.csv Test\ #09\ \(Conv.\)\ -\ AWS/
mv T1-GreedyConvergence07-AWS-1500-2.csv Test\ #09\ \(Conv.\)\ -\ AWS/
mv T1-RandomConvergence07-AWS-1500-1.csv Test\ #09\ \(Conv.\)\ -\ AWS/
mv T1-RandomConvergence07-AWS-1500-2.csv Test\ #09\ \(Conv.\)\ -\ AWS/
mv T1-GreedyConvergence09-AWS-1500-1.csv Test\ #09\ \(Conv.\)\ -\ AWS/
mv T1-GreedyConvergence09-AWS-1500-2.csv Test\ #09\ \(Conv.\)\ -\ AWS/
mv T1-RandomConvergence09-AWS-1500-1.csv Test\ #09\ \(Conv.\)\ -\ AWS/
mv T1-RandomConvergence09-AWS-1500-2.csv Test\ #09\ \(Conv.\)\ -\ AWS/
mv T1-GreedyConvergence11-AWS-1500-1.csv Test\ #09\ \(Conv.\)\ -\ AWS/
mv T1-GreedyConvergence11-AWS-1500-2.csv Test\ #09\ \(Conv.\)\ -\ AWS/
mv T1-RandomConvergence11-AWS-1500-1.csv Test\ #09\ \(Conv.\)\ -\ AWS/
mv T1-RandomConvergence11-AWS-1500-2.csv Test\ #09\ \(Conv.\)\ -\ AWS/
rm AWS-T1-Convergence.sh

echo "T#10 - GeSeMa Timing Test"
cp Test\ #10\ \(Tim.\)\ -\ AWS/AWS-T2-Timing.sh ./
chmod +x AWS-T2-Timing.sh
./AWS-T2-Timing.sh
mv AWS_REQ_7TIMING.csv Test\ #10\ \(Tim.\)\ -\ AWS/
mv AWS_REQ_9TIMING.csv Test\ #10\ \(Tim.\)\ -\ AWS/
mv AWS_REQ_11TIMING.csv Test\ #10\ \(Tim.\)\ -\ AWS/
rm AWS-T2-Timing.sh

echo "T#11 - Classic Comparison Pareto Test"
cp Test\ #11\ \(P.\ Comp.\)\ -\ AWS/AWS-T3-Compare.sh ./
chmod +x AWS-T3-Compare.sh
./AWS-T3-Compare.sh
mv AWS_REQ_7RELQUALITY.csv Test\ #11\ \(P.\ Comp.\)\ -\ AWS/
mv AWS_REQ_9RELQUALITY.csv Test\ #11\ \(P.\ Comp.\)\ -\ AWS/
mv AWS_REQ_11RELQUALITY.csv Test\ #11\ \(P.\ Comp.\)\ -\ AWS/
rm AWS-T3-Compare.sh

echo "T#11.2 - Classic Comparison Pareto Test (time 10s)"
cp Test\ #11.2\ \(P.\ Comp.\)\ -\ AWS/AWS-T3.2-Compare.sh ./
chmod +x AWS-T3.2-Compare.sh
./AWS-T3.2-Compare.sh
mv AWS_REQ_7RELQUALITY.csv Test\ #11.2\ \(P.\ Comp.\)\ -\ AWS/
mv AWS_REQ_9RELQUALITY.csv Test\ #11.2\ \(P.\ Comp.\)\ -\ AWS/
mv AWS_REQ_11RELQUALITY.csv Test\ #11.2\ \(P.\ Comp.\)\ -\ AWS/
rm AWS-T3.2-Compare.sh

echo "T#12 - Classic Comparison Timing Test"
cp Test\ #12\ \(T.\ Comp\)\ -\ AWS/AWS-T4-Timing.sh ./
chmod +x AWS-T4-Timing.sh
./AWS-T4-Timing.sh
mv AWS_REQ_7TIMING.csv Test\ #12\ \(T.\ Comp\)\ -\ AWS/
mv AWS_REQ_9TIMING.csv Test\ #12\ \(T.\ Comp\)\ -\ AWS/
mv AWS_REQ_11TIMING.csv Test\ #12\ \(T.\ Comp\)\ -\ AWS/
rm AWS-T4-Timing.sh

echo "T#13 - SPEA/NSGA GeSeMa Pareto Test"
cp Test\ #13\ \(NS\ P.\ Comp\)\ -\ AWS/AWS-T5-Algorithm.sh ./
chmod +x AWS-T5-Algorithm.sh
./AWS-T5-Algorithm.sh
mv AWS_REQ_7RELQUALITY.csv Test\ #13\ \(NS\ P.\ Comp\)\ -\ AWS/
mv AWS_REQ_9RELQUALITY.csv Test\ #13\ \(NS\ P.\ Comp\)\ -\ AWS/
mv AWS_REQ_11RELQUALITY.csv Test\ #13\ \(NS\ P.\ Comp\)\ -\ AWS/
rm AWS-T5-Algorithm.sh

echo "T#14 - SPEA/NSGA GeSeMa Timing Test"
cp Test\ #14\ \(NS\ T.\ Comp\)\ -\ AWS/AWS-T6-Algorithm.sh ./
chmod +x AWS-T6-Algorithm.sh
./AWS-T6-Algorithm.sh
mv AWS_REQ_7TIMING.csv Test\ #14\ \(NS\ T.\ Comp\)\ -\ AWS/
mv AWS_REQ_9TIMING.csv Test\ #14\ \(NS\ T.\ Comp\)\ -\ AWS/
mv AWS_REQ_11TIMING.csv Test\ #14\ \(NS\ T.\ Comp\)\ -\ AWS/
rm AWS-T6-Algorithm.sh

echo "T#15 - GA+LCB GeSeMa Pareto Test"
cp Test\ #15\ \(GA+LCB\ P.\ Comp.\)\ -\ AWS/AWS-T7-Compare.sh ./
chmod +x AWS-T7-Compare.sh
sudo sh AWS-T7-Compare.sh
mv AWS_REQ_7_GALCBRELQUALITY.csv Test\ #15\ \(GA+LCB\ P.\ Comp.\)\ -\ AWS/
mv AWS_REQ_9_GALCBRELQUALITY.csv Test\ #15\ \(GA+LCB\ P.\ Comp.\)\ -\ AWS/
mv AWS_REQ_11_GALCBRELQUALITY.csv Test\ #15\ \(GA+LCB\ P.\ Comp.\)\ -\ AWS/
rm AWS-T7-Compare.sh

echo "T#16 - GA+LCB GeSeMa Timing Test"
cp Test\ #16\ \(GA+LCB\ T.\ Comp\)\ -\ AWS/AWS-T8-Timing.sh ./
chmod +x AWS-T8-Timing.sh
./AWS-T8-Timing.sh
mv AWS_REQ_7_GALCBTIMING.csv Test\ #16\ \(GA+LCB\ T.\ Comp\)\ -\ AWS/
mv AWS_REQ_9_GALCBTIMING.csv Test\ #16\ \(GA+LCB\ T.\ Comp\)\ -\ AWS/
mv AWS_REQ_11_GALCBTIMING.csv Test\ #16\ \(GA+LCB\ T.\ Comp\)\ -\ AWS/
rm AWS-T8-Timing.sh

rm AWS_REQ_7.yaml
rm AWS_REQ_9.yaml
rm AWS_REQ_11.yaml

rm AWS_REQ_7_GALCB.yaml
rm AWS_REQ_9_GALCB.yaml
rm AWS_REQ_11_GALCB.yaml

rm 1.Exhaustive.py
rm 2.Random.py
rm 3.Greedy.py
rm 4.SK-Greedy.py
rm 5.GeSeMa.py
rm 6.GA+LCB.py

rm TestFramework.py
