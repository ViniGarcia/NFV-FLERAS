NFV FLERAS: NFV FLExible Resource Allocation System
========================================================

*Status: Development*

### What is FLERAS?

FLERAS is a system to execute NFV Resource Allocation (NFV RA) [1] processes. To do that, 
FLERAS uses an innovative SFC Request model (structure using YAML) to flexibilize the 
definition of goal functions and policies to be applied during the NFV RA processing. 
In addition to the new SFC Request, FLERAS provides a formal and simple SFC topology 
specification method based on a context-free grammar. FLERAS is especially indicating 
to evaluate different goal functions under a generic SFC Composition and SFC Split and 
Mapping solution.<br/>
<br/>
The FLERAS' request model is structure by a YAML notation and presents three main blocks:<br/>
1. METADATA BLOCK<br/>
1.1. ID (Request unique identifier)<br/>
1.2. DESCRIPTION (Multi line request description)<br/>
2. GOAL FUNCTION BLOCK<br/>
2.1. GOAL (Minimize ("MIN") or maximize ("MAX") metrics)<br/>
2.2. FUNCTION (Evaluation metrics description)<br/>
2.2.1. METRIC (Metric unique identifier)<br/>
2.2.2. WEIGHT (Value for weighted evaluation)<br/>
2.2.3. INPUT (Initial metric value)<br/>
2.2.4. EVALUATION (Metric evaluation operation ("MULT", "DIV", "SUM", "SUB"))<br/>
2.2.5. UPDATE (Metric ID that the evaluation operation will update this metric)<br/>
3. TOPOLOGY FUNCTION BLOCK<br/>
3.1. TOPOLOGY (Topology defined with the context-free grammar described below)<br/>
3.2. BRANCHINGS (List of lists indicating the expected traffic splitting in branchs segments - topology opening linear order)<br/>
3.3. OPELEMENTS<br/>
3.3.1. ID (Operational element unique ID)<br/>
3.3.2. METRICS ID (Indicates the evaluation/update factor for each metric)<br/>
3.4. EPS (List of EPs)<br/>
3.4.1. ID (EP unique identifier)<br/>

The FLERAS SFC specification follows the context-free grammar production rules:<br/>
1. S -> "IP" OPBLOCK<br/>
2. OPBLOCK -> TBRANCH | NTBRANCH | TPBLOCK OPBLOCK | TPBLOCK EP<br/>
3. ROPBLOCK -> INTBRANCH | TPBLOCK ROPBLOCK | TPBLOCK<br/>
4. TPBLOCK -> PORDER | OPELEM<br/>
5. PORDER -> "[" OPELEM NOPELEM "]" POEXCEPTION | "[" OPELEM NOPELEM "]"<br/>
6. POEXCEPTION -> "(" OPELEM OPELEM ")" POEXCEPTION | "(" OPELEM OPELEM ")" | "(" OPELEM OPELEM "*" ")" POEXCEPTION | "(" OPELEM OPELEM "*" ")"<br/>
7. TBRANCH -> TPBLOCK "{" OPBLOCK NEXTTBRANCH "}"<br/>
8. NEXTTBRANCH -> "/" OPBLOCK NEXTTBRANCH | "/" OPBLOCK<br/>
9. NTBRANCH -> TPBLOCK "{" ROPBLOCK NEXTNTBRANCH "}" OPBLOCK<br/>
10. INTBRANCH -> TPBLOCK "{" ROPBLOCK NEXTNTBRANCH "}" ROPBLOCK<br/>
11. NEXTNTBRANCH -> "/" ROPBLOCK NEXTNTBRANCH | "/" ROPBLOCK<br/>
12. NOPELEM -> OPELEM NOPELEM | OPELEM<br/>
13. OPELEM -> OPEID1, OPEID2, ..., OPEIDN*<br/>
14. EP -> EPID1, EPID2, ..., EPIDN*<br/>
<br/>
*Retrieved from the FLERAS request.

### How was it developed?

FLERAS is being developed using standard Python 3 language and other libraries such as:<br/>
1. Natural Languege Tool Kit (pip3 install nltk)<br/>
2. Python YAML (pip3 install pyyaml)

### Project steps

1. SFC topology validator (OK!!)<br/>
2. SFC request validator (OK!!)<br/>
3. SFC expansion tool (IN DEVELOPMENT!!)<br/>
4. SFC goal function creator (WAITING)<br/>
5. SFC generic composition method (WAITING)<br/>
6. SFC generic split and mapping method (WAITING)<br/>
7. SFC generic selection method (WAITING)<br/>
8. SFC registry architecture (WAITING)<br/>
9. Graphical interface (WAITING)

### Support

Contact us towards git issues requests or by the e-mail vfulber@inf.ufsm.br.

### NIEP Research Group

Vinícius Fülber Garcia (Federal University of Santa Maria - Brazil)<br/>
Carlos Raniery Paula dos Santos (Federal University of Santa Maria - Brazil)

### References

-> NFV Resource Allocation <-<br/>
[1] J. Gil Herrera and J. F. Botero, "Resource Allocation in NFV: A Comprehensive Survey," in IEEE Transactions on Network and Service Management, vol. 13, no. 3, pp. 518-532, Sept. 2016. doi: 10.1109/TNSM.2016.2598420