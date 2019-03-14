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

<!---
The FLERAS' request model is structure by a YAML notation and presents three main blocks:<br/>
1. METADATA BLOCK<br/>
1.1. ID (Request unique identifier)<br/>
1.2. DESCRIPTION (Multi line request description)<br/>
2. SERVICE BLOCK<br/>
2.1. TOPOLOGY (Topology defined with the context-free grammar described below)<br/>
2.2. OELEMENTS (List of operacional elements IDs)<br/>
2.3. OUTNODES (List of output nodes IDs)<br/>
3. GOAL FUNCTION BLOCK<br/>
3.1. METRICS (List of metric objects that composes the goal function)<br/>
3.1.1. ID (Metric unique identifier)<br/>
3.1.2. GOAL (Minimize ("MIN") or maximize ("MAX") metric)<br/>
3.1.3. WEIGHT (Value for weighted evaluation)<br/>
3.1.4. INPUT (Initial metric value)<br/>
3.1.5. EVALUATION (Metric evaluation operation ("MULT", "DIV", "SUM", "SUB"))<br/>
3.1.6. UPDATE (Metric ID that the evaluation operation will update this metric)<br/>
3.2. BRANCHINGS (List of evaluation data division between segments of ramifications for every metric)<br/>
3.2.1. METRIC (Some metric ID)<br/>
3.2.1.1. UPDATE (Metric evaluatin data division operation ("MULT", "DIV", "SUM", "SUB"))<br/>
3.2.1.2. FACTORS (Metric evaluation data division factors, a list with one factor for each segment in the branchings and one list per branching)<br/>
4. POLICIES ()<br/>
4.1. IMMEDIATE ()<br/>
4.1.1. ID ()<br/>
4.1.2. MIN ()<br/>
4.1.3. MAX ()<br/>
4.1.4. TYPE ()<br/>
4.1.5. GOAL ()<br/>
4.1.6. WEIGHT ()<br/>
4.2. AGGREGATE ()<br/>
4.2.1. ID ()<br/>
4.2.2. MIN ()<br/>
4.2.3. MAX ()<br/>
4.2.4. TYPE ()<br/>
4.2.5. GOAL ()<br/>
4.2.6. WEIGHT ()<br/>
5. DEPLOYMENT ()<br/>
5.1. OELEMENT ()<br/>
5.1.1. FLAVOUR ()<br/>
5.1.1.1. MEMORY ()<br/>
5.1.1.2. NET_IFACES ()<br/>
5.1.1.3. CPUS ()<br/>
5.1.2. BENCHMARK ()<br/>
5.1.2.1. METRIC () <br/>

The FLERAS SFC specification follows the context-free grammar production rules:<br/>
1. S -> "IP" OPBLOCK<br/>
2. OPBLOCK -> TBRANCH | NTBRANCH | TPBLOCK OPBLOCK | TPBLOCK EP<br/>
3. ROPBLOCK -> INTBRANCH | TPBLOCK ROPBLOCK | TPBLOCK<br/>
4. TPBLOCK -> PORDER | MASKPELEM<br/>
5. PORDER -> "[" MASKPELEM NPELEM "]" POEXCEPTION | "[" MASKPELEM NPELEM "]"<br/>
6. POEXCEPTION -> "(" PELEM PELEM ")" POEXCEPTION | "(" PELEM PELEM ")" | "(" PELEM PELEM "*" ")" POEXCEPTION | "(" PELEM PELEM "*" ")"<br/>
7. TBRANCH -> TPBLOCK "{" OPBLOCK NEXTTBRANCH "}" <br/>
8. NEXTTBRANCH -> "/" OPBLOCK NEXTTBRANCH | "/" OPBLOCK<br/>
9. NTBRANCH -> TPBLOCK "{" ROPBLOCK NEXTNTBRANCH "}" OPBLOCK<br/>
10. INTBRANCH -> TPBLOCK "{" ROPBLOCK NEXTNTBRANCH "}" ROPBLOCK<br/>
11. NEXTNTBRANCH -> "/" ROPBLOCK NEXTNTBRANCH | "/" ROPBLOCK<br/>
12. NPELEM -> MASKPELEM NPELEM | MASKPELEM<br/>
13. MASKPELEM -> PELEM | PELEM "<" DOMAIN ">"<br/>
14. OPELEM -> OPEID1, OPEID2, ..., OPEIDn*<br/>
15. EP -> EPID1, EPID2, ..., EPIDn*<br/>
16. DOMAIN -> DOMID1, DOMID2, ..., DOMIn*<br/>

*Retrieved from the FLERAS request.
-->

### How was it developed?

FLERAS is being developed using standard Python 3 language and other libraries such as:<br/>
1. Natural Languege Tool Kit (pip3 install nltk)<br/>
2. Python YAML (pip3 install pyyaml)

### Project steps

1. SFC topology validator (OK!!)<br/>
2. SFC request validator (OK!!)<br/>
3. SFC expansion tool (OK!!)<br/>
4. SFC goal function creator (OK!!)<br/>
5. SFC generic composition method (OK!!)<br/>
6. SFC generic split and mapping method (IN DEVELOPMENT!!)<br/>
7. SFC generic selection method (WAITING)<br/>
8. SFC registry architecture (WAITING)<br/>
9. Graphical interface (WAITING)

### Support

Contact us towards git issues requests or by the e-mail vfulber@inf.ufsm.br.

### FLERAS Research Group

Vinícius Fülber Garcia (Federal University of Santa Maria - Brazil)<br/>
Carlos Raniery Paula dos Santos (Federal University of Santa Maria - Brazil)

### References

-> NFV Resource Allocation <-<br/>
[1] J. Gil Herrera and J. F. Botero, "Resource Allocation in NFV: A Comprehensive Survey," in IEEE Transactions on Network and Service Management, vol. 13, no. 3, pp. 518-532, Sept. 2016. doi: 10.1109/TNSM.2016.2598420
