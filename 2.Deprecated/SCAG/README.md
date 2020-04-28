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

<p align="center">
  <img src="http://www.inf.ufpr.br/vfgarcia/hosting/SCAG.png">
</p>

### Do you have some examples?

<p align="justify">Yes, for sure. First, let us specify the media cache service presented in [1]. This service is a simple linear topology with three network functions: Cache (C), Firewall (FW), and Network Address Translator (NAT). This service is depicted in the figure below [A]. The SCAG specification is shown in the same figure in [B]. Note that the symbol "EN1" defines an egress node.</p>

<p align="center">
  <img src="http://www.inf.ufpr.br/vfgarcia/hosting/MS.png">
</p>

<p align="justify">However, sometimes, branching segments are needed. An example where branching is requested is the security service presented in [2]. This security topology is composed of multiple branches that process suspicious traffic according to the type and the network layer of threat. We depict the described service topology in the figure below in [A] with four network functions: Screener (S), Network Security (NS -- for layer 3 threats), Application Security (AS - for layer 7 threats), and Network Adress Translator (NAT). In figure [B], we show the SCAG specification with three egress nodes (EN1, EN2, and EN3).</p>

<p align="center">
  <img src="http://www.inf.ufpr.br/vfgarcia/hosting/SS.png">
</p>

<p align="justify">Finally, when a service topology is submitted to a composing solution, the network operator should be able to previous declare partially ordered segments of network functions. Thus, these segments become the optimization target of composing solutions. For example, consider an HTTP security service with five network functions as depicted in figure below [A]: Firewall (FW), Deep Packet Inspector (DPI), Markup Filter (MF), Intrusion Prevent System (IPS), and Load Balancer (LB). The first four functions (FW, DPI, MF, and IPS) can be repositioned (with some constraints, discussed later) and still provide the same service functionalities. Note that there are some constraints to be observed, for example, the MF is coupled to the DPI once the DPI mark invalid requests and the MF drops them. Also, the FW has an ordering dependency with the DPI once only HTTP packets are allowed by the firewall, and the DPI is designed to analyze only this protocol. In figure [B], the SCAG specification of the described service and its partially ordering segments/dependencies is presented.</p>

<p align="center">
  <img src="http://www.inf.ufpr.br/vfgarcia/hosting/HSS.png">
</p>
