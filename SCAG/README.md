SCAG: Service ChAin Grammar
========================================================

*Status: Stable - 1.0*

### What is SCAG?

<p align="justify">SCAG simplified version of CUSTOM. It is a context-free grammar for the specification of service topologies. In addition to a variety of service topology structures, such as partially ordered segments, terminal branchings, and non-terminal branchings, SCAG foresees the definition of network function dependencies and administrative domain dependencies (information processed during the service deployment). We provide a complete Python 3 validator for SCAG specifications. This validator analyzes the provided service topology syntactically and semantically, thus ensuring its correctness according to grammar rules and some other criteria (*e.g.*, impossible dependencies and topology cycles).</p>

### How was it developed?

SCAG was developed using standard Python 3 language and other libraries such as:<br/>
1. Natural Languege Tool Kit (pip3 install nltk)<br/>
2. Python YAML (pip3 install pyyaml)

### How does it work?

<p align="justify">SCAG specifies service topologies as linear texts. It enables the network operators to define partially ordered segments to be computed in the composing task of the deployment process. These segments can have some constraints defines as ordering dependencies (precedence between two functions) and coupling dependencies (the mandatory connection between two functions). Furthermore, it is possible to specify terminal branchings (with branch segments which never intersect and ends in an egress node) and non-terminal branchings (with branch segments without any egress node and with a common intersection point). Network functions (VNFs as well as PNFs) can be defined in the rule of processing elements (PELEM), each function can carry, if necessary, an administrative domain dependency. Available administrative domains, in turn, are allocated in rule DOMAIN. Finally, egress nodes are present in rule EN. Observe that PELEM, EN, and DOMAIN are on-demand defined by the validators users. The figure below depicts the grammatic rules.</p>

![alt text](http://www.inf.ufpr.br/vfgarcia/hosting/SCAG.png)
