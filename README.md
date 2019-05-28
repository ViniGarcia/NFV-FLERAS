NFV FLERAS: NFV FLExible Resource Allocation System
========================================================

*Status: Development*

### What is FLERAS?

<p style=”text-align: justify;”>FLERAS is a system to execute NFV Resource Allocation (NFV-RA) [1] processes. To do that, FLERAS uses a novel NFV service request model (structured in YAML) that relaxes the definition of goal functions and policies used for the NFV-RA execution. Furthermore, FLERAS provides a formal and robust NFV service topology specification model based on a context-free grammar (SCAG -- simplified version --- or CUSTOM -- complete version). Finally, a new generic evaluation method (i.e., can be employed in any deployment stage) based on indexing is also presented to jointly evaluate many metrics with different granularity and objectives that forms objective functions. This methodology reduces every evaluation problem into an index maximization problem, providing an unified result (Suitability Index) for each deployment candidate. FLERAS is a work in progress, new tools and models will be updated in this GitHub.</p><br/>
<br/>

### How was it developed?

FLERAS is being developed using standard Python 3 language and other libraries such as:<br/>
1. Natural Languege Tool Kit (pip3 install nltk)<br/>
2. Python YAML (pip3 install pyyaml)

### Project steps

1. NFV service topology validator [OK!!]<br/>
2. NFV service request validator [OK!!]<br/>
3. NFV service topology expansion tool (deployment composing stage) [OK!!]<br/>
4. NFV composing goal function creator (deployment composing stage) [OK!!]<br/>
5. NFV service generic composition tool (deployment composing stage) [OK!!]<br/>
6. NFV service generic split and mapping tool (deployment embedding stage) [IN DEVELOPMENT!!]<br/>
7. NFV service generic selection tool (deployment embedding stage) [WAITING]<br/>
8. NFV service generic placement tool (deployment embedding stage) [WAITING]<br/>
8. NFV service generic scheduling tool (deployment scheduling stage) [WAITING]<br/>
8. Deployment-as-a-Service architecture (NFV market integration) [WAITING]<br/>
9. Graphical interface [WAITING]

### Support

Contact us towards git issues requests or by the e-mail vfulber@inf.ufsm.br.

### FLERAS Research Group

Vinícius Fülber Garcia (Federal University of Paraná - Brazil)<br/>
Elias Procópio Duarte Júnior (Federal University of Paraná - Brazil)<br/>
Carlos Raniery Paula dos Santos (Federal University of Santa Maria - Brazil)<br/>
Marcelo Caggiani Luizelli (Federal University of Pampa - Brazil)<br/>

### Publications

**-> Uma Solução Flexível e Personalizável para a Composição de Cadeias de Função de Serviço <-<br/>**
V. F. Garcia and M. C. Luizelli and E. P. Duarte Junior and C. R. P. dos Santos, "Uma Solução Flexível e Personalizável para a Composição de Cadeias de Função de Serviço," in XXIV Workshop de Gerência e Operações de Redes e Serviços (XXXVII Simpósio Brasileiro de Redes e Sistemas Distribuídos), pp. 101-114, May. 2019. link: http://sbrc2019.sbc.org.br/wp-content/uploads/2019/05/wgrs2019.pdf  

### References

**-> NFV Resource Allocation <-<br/>**
[1] J. Gil Herrera and J. F. Botero, "Resource Allocation in NFV: A Comprehensive Survey," in IEEE Transactions on Network and Service Management, vol. 13, no. 3, pp. 518-532, Sept. 2016. doi: 10.1109/TNSM.2016.2598420
