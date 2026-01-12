# Instruções Para a Reprodução dos Testes

### Artigo: *Do Tronco às Folhas: Evoluindo o Remapeamento de Serviços de Rede NFV com Algoritmos Genéticos Sensíveis ao Histórico*

### Simpósio Brasileiro de Redes de Computadores e Sistemas Distribuídos (SBRC 2026)

## Organização
Os arquivos utilizados e gerados neste experimento estão organizados da seguinte forma:
> `tronco-testes`
>
>> `35x11`
>>
>> `FrameworkGeSeMa`

No diretório `35x11` encontram-se os seguintes arquivos e subdiretórios:
* *35x11.yaml*: arquivo base de entrada do GeSeMa utilizado para a geração do histórico e das modificações de cada caso;
* *35x11-modified-cases.log*: arquivo que registra todas as modificações realizadas no ambiente;
* `Mod_n`: diretórios que armazenam os respectivos arquivos de entrada do GeSeMa, para o mapeamento e remapeamento, de acordo com as modificações feitas no ambiente;
* `heritage_base`: arquivos referentes aos dados históricos utilizados. *output-[0]-unified.csv*, arquivo original proveniente de 30 execuções do GeSeMa; `bests`, contendo a seleção das melhores fronteiras de Pareto segundo sua média; e `random`, contendo a seleção de forma aleatória; 
* `h1`, `h2`, `h3` e `h4`: respectivos diretórios dos casos 1, 2, 3 e 4. Seus subdiretórios estão organizados entre as melhores fronteiras `heritage_bests` e as aleatórias `heritage_random`. Em cada um deles é possível encontrar os arquivos de saída gerados pelo `FrameworkGeSeMa`. A fim de auxiliar a análise dos dados, os aquivos sumary-Mod_n.csv foram gerados apenas sumarizando as saídas pertinentes.

Já no diretório `FrameworkGeSeMa` estão o *framework* desenvolvido para a execução e a comparação dos testes e os *scripts* que realizam a automação para casos citados anteriormente.

## Reprodução
Para a reprodução de cada caso de teste, é necessário executar os *scripts* presentes no diretório `FrameworkGeSeMa`: *run-tests-h1.sh*, *run-tests-h2.sh*, *run-tests-h3.sh* e *run-tests-h4.sh*. Cada um deles está configurado para a correta execução do *framework* de teste, ou seja, o arquivo *TestFramework.py* e seus argumentos.

Os respectivos arquivos de saída, *RELQUALITY.csv*, são movidos ao final de cada teste para seu respectivo diretório ($target).

Obs.: é necessário que cada arquivo *.sh* tenha a permissão de execução no sistema.

## Ambiente de Execução
Os resultados provenientes dos testes apresentados no artigo são de um ambiente computacional com as seguintes configurações:
* Intel Core i7-1355U;
* 16GB de RAM (DDR4, 3.200 MT/s);
* Ubuntu 24.04.3 LTS (kernel 6.14.0-37-generic);
* Python 3.12.3.

