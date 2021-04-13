NFV FLERAS: NFV FLExible Resource Allocation System
========================================================

*Status: Development*

### What is FLERAS?

<p align="justify">FLERAS is a system to execute NFV Resource Allocation (NFV-RA) [1] processes. To do that, FLERAS uses a novel NFV service request model (structured in YAML) that relaxes the definition of goal functions and policies used for the NFV-RA execution. Furthermore, FLERAS provides a formal and robust NFV service topology specification model based on a context-free grammar (SCAG -- simplified version --- or CUSTOM -- complete version). Finally, a new generic evaluation method (i.e., can be employed in any deployment stage) based on indexing is also presented to jointly evaluate many metrics with different granularity and objectives that forms objective functions. This methodology reduces every multiple evaluation problems into a unique index maximization problem, thus providing a unified result (Suitability Index) for each deployment candidate. FLERAS is a work in progress, new tools and models, as well as papers and presentation, will be updated in this GitHub.</p>

### Important information!

<p align="justify"> Currently, FLERAS uses CUSTOM to specify network service topologies. However, CUSCO, CUSMAP, and GeSeMa enable a limited subset of specification capabilities from CUSTOM (called SCAG). The particular implementation of SCAG is deprecated since the release of CUSTOM, but for the usage of currently available customizable deployment solutions, consider the SCAG production rules to specify the service topologies (these rules are available in 2.Deprecated/SCAG).</p>

### How was it developed?

FLERAS is being developed using standard Python 3 language and other libraries such as:<br/>
1. Natural Languege Tool Kit (pip3 install nltk)<br/>
2. Python YAML (pip3 install pyyaml)
3. NumPy (pip3 install numpy)

### Project steps

1. NFV service topology validator [OK!!]<br/>
2. NFV service request validator [OK!!]<br/>
3. NFV service topology expansion tool (deployment composing stage) [OK!!]<br/>
4. NFV composing goal function creator (deployment composing stage) [OK!!]<br/>
5. NFV service generic composition tool (deployment composing stage) [OK!!]<br/>
6. NFV service generic split and mapping tool (deployment embedding stage) [OK!!]<br/>
7. NFV service generic selection tool (deployment embedding stage) [WAITING]<br/>
8. NFV service generic placement tool (deployment embedding stage) [WAITING]<br/>
8. NFV service generic scheduling tool (deployment scheduling stage) [WAITING]<br/>
8. Deployment-as-a-Service architecture (NFV market integration) [WAITING]<br/>
9. Graphical interface [WAITING]

### Project details

1. YAMLR (YAML Request): NFV service request model
2. SCAG (Service ChAin Grammar): simple NFV service topology specification model
3. CUSTOM (CUtomazable Service Topology Model): complete NFV service topology specification model
4. CHEF (Classification and Holistic Evaluation Framework): multi-criteria and holistic deployment evaluation/classification framework
5. CUSCO (CUstomazable Service COmposing): generic and flexible composition tool
6. CUSMAP (CUstomazable Service MAPping): generic and flexible split and mapping tool
7. GESEMA (GEnetic SErvice MApping): generic and flexible genetic heuristic for split and mapping (standalone -- not integrated yet)

### Support

Contact us towards git issues requests or by the e-mail vfulber@inf.ufsm.br.

### FLERAS Research Group

Vinícius Fülber Garcia (Federal University of Paraná - Brazil)<br/>
Alexandre Huff (Federal Technological University of Paraná - Brazil)<br/>
Leonardo da Cruz Marcuzzo (Federal University of Santa Maria - Brazil)<br/>
Lisandro Zambenedetti Granville (Federal University of Porto Alegre - Brazil)<br/>
Alberto Egon Schaeffer-Filho (Federal University of Porto Alegre - Brazil)<br/>
Marcelo Caggiani Luizelli (Federal University of Pampa - Brazil)<br/>
Carlos Raniery Paula dos Santos (Federal University of Santa Maria - Brazil)<br/>
Eduardo Jaques Spinosa (Federal University of Paraná - Brazil)<br/>
Elias Procópio Duarte Júnior (Federal University of Paraná - Brazil)<br/>

### Publications

<p align="justify">V. F. Garcia; M. C. Luizelli; E. P. Duarte Junior; C. R. P. dos Santos, "Uma Solução Flexível e Personalizável para a Composição de Cadeias de Função de Serviço" in Workshop de Gerência e Operações de Redes e Serviços (Simpósio Brasileiro de Redes e Sistemas Distribuídos), pp. 101-114, May. 2019. link: http://sbrc2019.sbc.org.br/wp-content/uploads/2019/05/wgrs2019.pdf</p>
<p align="justify">Fulber-Garcia, V.; Luizelli, M. C.; Santos, C. R. P. d.; Duarte Jr., E. P., "CUSCO: A Customizable Solution for NFV Composition" in International Conference on Advanced Information Networking and Applications, pp. 204-216, Mar. 2020. link: https://link.springer.com/chapter/10.1007/978-3-030-44041-1_19</p>
<p align="justify">Fulber-Garcia, V.; Santos, C. R. P. d.; Spinosa, E. J.; Duarte Jr., E. P., "Mapeamento Customizado de Serviços de Rede em Múltiplos Domínios Baseado em Heurísticas Genéticas" in Simpósio Brasileiro de Redes e Sistemas Distribuídos, pp. 491-504, Dec. 2020. link: https://sol.sbc.org.br/index.php/sbrc/article/view/12304</p>
<p align="justify">Fulber-Garcia, V.; Huff, A.; Santos, C. R. P. d.; Duarte Jr., E. P., "Network Service Topology: Formalization, Taxonomy and the CUSTOM Specification Model" in Computer Networks (ComNet), vol. 178, pp. 107337, 2020. link: https://www.sciencedirect.com/science/article/abs/pii/S1389128619312460?casa_token=Vb4w4qejcVMAAAAA:1tdIVd1H6VKepc5r5Jl6nZe6dh7Lz-qP84fT-z-lLLoxbQ1cy1a2QU56Hxju9m7v1rjMpoyudhQ</p>
<p align="justify">Fulber-Garcia, V.; Huff, A.; Marcuzzo, L. d. C.; Luizelli, M. C.; Schaeffer-Filho, A. E.; Granville, L. Z.; Santos, C. R. P. d.; Duarte Jr., E. P., "Customizable Deployment of NFV Services" in Journal of Network and Systems Management (JNSM), vol. [TO APPEAR], pp. [TO APPEAR], 2021, link: [TO APPEAR].</p>

### References

<p align="justify">[1] J. Gil Herrera and J. F. Botero, "Resource Allocation in NFV: A Comprehensive Survey," in IEEE Transactions on Network and Service Management, vol. 13, no. 3, pp. 518-532, Sept. 2016. doi: 10.1109/TNSM.2016.2598420</p>
