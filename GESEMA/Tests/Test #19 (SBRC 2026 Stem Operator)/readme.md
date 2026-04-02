# Instruções Para a Reprodução dos Testes

### Artigo: *Tronco: Um Operador Genético para Remapeamento de Serviços de Rede Sensível ao Histórico*

### Simpósio Brasileiro de Redes de Computadores e Sistemas Distribuídos (SBRC 2026)

## Resumo
Uma das principais vantagens do paradigma da Virtualização de Funções de Rede (NFV) é a flexibilidade trazida para o núcleo da rede. Entretanto, é notável a lacuna de estratégias para o mapeamento de serviços de rede baseados em NFV que levam em conta que as redes de comunicações são dinâmicas, no sentido de que seu estado se altera gradualmente com o tempo. Por isso, este artigo apresenta um novo operador genético para o mapeamento dinâmico de serviços virtualizados em diferentes domínios e pontos de presença. Apesar de soluções de mapeamento baseadas em algoritmos genéticos apresentarem bons resultados para o processo de mapeamento inicial, elas desconsideram informações históricas para o remapeamento do serviço quando o estado da rede muda. O operador aqui proposto, denominado Tronco, utiliza dados históricos para garantir a otimalidade (local ou global) do remapeamento de serviços de rede. Os resultados experimentais de sua implementação são apresentados para diversos cenários, considerando: (i) o mesmo número de gerações; (ii) a execução até a convergência; e (iii) diferentes níveis de mudança no estado da rede. Os resultados demonstram melhorias significativas no remapeamento de serviços virtualizados com o uso do Tronco.

## Estrutura
Os arquivos utilizados e gerados neste experimento estão organizados da seguinte forma:
> `main`
>
>> `35x11`
>>
>> `FrameworkGeSeMa`

No diretório `35x11` encontram-se os seguintes arquivos e subdiretórios:
* *35x11.yaml*: arquivo base de entrada do GeSeMa utilizado para a geração do histórico e das modificações de cada cenário;
* *35x11-modified-cases.log*: arquivo que registra todas as modificações realizadas no ambiente;
* `Mod_n`: diretórios que armazenam os respectivos arquivos de entrada do GeSeMa, para o Remapeamento a Frio (RaF) e o Remapeamento com Tronco (RcT), de acordo com as modificações feitas no ambiente;
* `heritage_base`: arquivos referentes aos dados históricos utilizados. *output-[0]-unified.csv*, arquivo original proveniente de 30 execuções do GeSeMa; `bests`, contendo a seleção das melhores fronteiras de Pareto segundo sua média; e `random`, contendo a seleção de forma aleatória; 
* `h1`, `h2` e `h3`: respectivos diretórios dos cenários 1, 2 e 3. Seus subdiretórios estão organizados entre as melhores fronteiras `heritage_bests` e as aleatórias `heritage_random`. Em cada um deles é possível encontrar os arquivos de saída gerados pelo `FrameworkGeSeMa`. A fim de auxiliar a análise dos dados, os aquivos sumary-Mod_n.csv foram gerados apenas sumarizando as saídas pertinentes.

Já no diretório `FrameworkGeSeMa` estão o *framework* desenvolvido para a execução e a comparação dos testes e os *scripts* que realizam a automação para os cenários citados anteriormente.

## Selos Considerados
Os autores consideram os seguintes selos para o processo de avaliação:
* Artefatos Disponíveis (SeloD);
* Artefatos Funcionais (SeloF);
* Artefatos Sustentáveis (SeloS);
* Experimentos Reprodutíveis (SeloR).

## Ambiente de Execução e Dependências
Os resultados provenientes dos testes apresentados no artigo são de um ambiente computacional com as seguintes configurações:
* Intel Core i7-1355U;
* 16GB de RAM (DDR4, 3.200 MT/s);
* Ubuntu 24.04.3 LTS (kernel 6.14.0-37-generic);
* Python 3.12.3.

## Reprodução
Para a reprodução de cada cenário de teste, é necessário executar os *scripts* presentes no diretório `FrameworkGeSeMa`: *run-tests-h1.sh*, *run-tests-h2.sh* e *run-tests-h3.sh*. Cada um deles está configurado para a correta execução do *framework* de teste, ou seja, o arquivo *TestFramework.py* e seus argumentos.

Os respectivos arquivos de saída, *RELQUALITY.csv*, são movidos ao final de cada teste para seu respectivo diretório ($target).

Obs.: é necessário que cada arquivo *.sh* tenha a permissão de execução no sistema.

## Licença
Este projeto está licenciado sob a licença MIT. Consulte o arquivo [LICENSE](https://github.com/ViniGarcia/NFV-FLERAS/blob/GesemaExperiments/LICENSE) para mais detalhes.
