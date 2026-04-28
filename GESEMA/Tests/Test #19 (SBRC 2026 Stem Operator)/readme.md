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

## Informações Básicas
Os resultados provenientes dos testes apresentados no artigo são de um ambiente computacional com as seguintes configurações:
* Intel Core i7-1355U;
* 16GB de RAM (DDR4, 3.200 MT/s);
* Ubuntu 24.04.3 LTS (kernel 6.14.0-37-generic).

## Dependências
Para a reprodução dos experimentos é necessário que as seguintes bibliotecas e seus módulos externos estejam instalados:
* Python 3.12.3;
* Numpy.

### Python
Inicialmente, é necessário verificar se a biblioteca do Python está instalada e na versão correta com o seguinte comando:

```
python3 --version
```

A saída deve ser algo semelhante à mensagem: 
```
Python 3.12.3
```
Se a saída não for como a anterior, instalar com o comando:
```
sudo apt install python3.12
```

### Numpy
Em seguida, é ncessário verificar se o módulo Numpy está instalado:
```
sudo apt list --installed | grep python3-numpy
```
A saída deve conter algo próximo à: 
```
python3-numpy/noble,now 1:1.26.4+ds-6ubuntu1 amd64 [instalado]
```

Se a saída não for como a anterior, instalar o respectivo módulo com o comando:
```
sudo apt install python3-numpy
```

Também é requisitado que cada arquivo *.sh* tenha a permissão de execução no sistema. Para isso, execute o seguinte comando no terminal, estando no mesmo diretório dos arquivos:

```
sudo chmod +x run-tests-h1.sh run-tests-h2.sh run-tests-h3.sh
```

## Preocupações com Segurança
Não há.

## Instalação
É necessário que o diretório em que este readme está armazenado seja baixado para a máquina que irá executar o teste e sua estrutura seja mantida.

## Teste Mínimo
Ao executar o *script* `run-tests-h1.sh` com o comando a seguir, nenhum erro deverá ser retornado pela aplicação.

```
./run-tests-h1.sh
```

## Experimentos
Cada um dos *scripts* de execução está configurado para a correta execução do *framework* de teste, ou seja, o arquivo *TestFramework.py* e seus argumentos. Os respectivos arquivos de saída, *RELQUALITY.csv*, são renomeados e movidos ao final de cada teste para seu respectivo diretório ($target).

Para a reprodução de cada cenário de teste, é necessário executar os *scripts* presentes no diretório `FrameworkGeSeMa`: 

### Reivindicação 1 (Cenário 1)
Para sua execução é necessário realizar o seguinte comando:
```
./run-tests-h1.sh
```
Os seguintes arquivos de saída, após a finalização da execução, serão movidos automaticamente para seus respectivos diretórios:
* Melhores Fronteiras `/35x11/h1/heritage_bests`: 
    * 35x11-Mod_5-RELQUALITY(g_30000-p_100-h_30-bests-50%).csv;
    * 35x11-Mod_5-RELQUALITY(g_30000-p_100-h_30-bests-100%).csv; 
    * 35x11-Mod_6-RELQUALITY(g_30000-p_100-h_30-bests-50%).csv;
    * 35x11-Mod_6-RELQUALITY(g_30000-p_100-h_30-bests-100%).csv.
* Fronteiras Aleatórias `/35x11/h1/heritage_random`: 
    * 35x11-Mod_5-RELQUALITY(g_30000-p_100-h_30-random-50%).csv;
    * 35x11-Mod_5-RELQUALITY(g_30000-p_100-h_30-random-100%).csv;
    * 35x11-Mod_6-RELQUALITY(g_30000-p_100-h_30-random-50%).csv;
    * 35x11-Mod_6-RELQUALITY(g_30000-p_100-h_30-random-100%).csv.

O tempo médio de execução desse cenário é de 145 minutos.

A **Figura 2. Cenário 1: Média das Fronteiras Relativas** presente no artigo ilustra os resultados extraídos dos arquivos de saída acima da seguinte forma:

* A **Subfigura 2.a 5% de Domínios Aprimorados** apresenta os valores dos arquivos cuja modificação é descrita por Mod_5. Aqui as colunas `MEAN_PARETO_G` e `STDEV_PARETO_G` serviram de base para o cálculo do intervalo de confiança de 95%;

* A **Subfigura 2.b 10% de Domínios Aprimorados** apresenta os valores dos arquivos cuja modificação é descrita por Mod_6. Aqui as colunas `MEAN_PARETO_G` e `STDEV_PARETO_G` também serviram de base para o cálculo do intervalo de confiança de 95%.

### Reivindicação 2 (Cenário 2)
Para sua execução é necessário realizar o seguinte comando:
```
./run-tests-h2.sh
```
Os seguintes arquivos de saída, após a finalização da execução, serão movidos automaticamente para seus respectivos diretórios:
* Melhores Fronteiras `/35x11/h2/heritage_bests`: 
    * 35x11-Mod_7-RELQUALITY(g_30000-p_100-h_30-bests-50%).csv;
    * 35x11-Mod_7-RELQUALITY(g_30000-p_100-h_30-bests-100%).csv;
    * 35x11-Mod_8-RELQUALITY(g_30000-p_100-h_30-bests-50%).csv;
    * 35x11-Mod_8-RELQUALITY(g_30000-p_100-h_30-bests-100%).csv;
    * 35x11-Mod_9-RELQUALITY(g_30000-p_100-h_30-bests-50%).csv;
    * 35x11-Mod_9-RELQUALITY(g_30000-p_100-h_30-bests-100%).csv;
    * 35x11-Mod_10-RELQUALITY(g_30000-p_100-h_30-bests-50%).csv;
    * 35x11-Mod_10-RELQUALITY(g_30000-p_100-h_30-bests-100%).csv.
* Fronteiras Aleatórias `/35x11/h2/heritage_random`:
    * 35x11-Mod_7-RELQUALITY(g_30000-p_100-h_30-random-50%).csv;
    * 35x11-Mod_7-RELQUALITY(g_30000-p_100-h_30-random-100%).csv;
    * 35x11-Mod_8-RELQUALITY(g_30000-p_100-h_30-random-50%).csv;
    * 35x11-Mod_8-RELQUALITY(g_30000-p_100-h_30-random-100%).csv;
    * 35x11-Mod_9-RELQUALITY(g_30000-p_100-h_30-random-50%).csv;
    * 35x11-Mod_9-RELQUALITY(g_30000-p_100-h_30-random-100%).csv;
    * 35x11-Mod_10-RELQUALITY(g_30000-p_100-h_30-random-50%).csv;
    * 35x11-Mod_10-RELQUALITY(g_30000-p_100-h_30-random-100%).csv.

O tempo médio de execução desse cenário é de 120 minutos.

A **Figura 3. Cenário 2: Média das Fronteiras Relativas** presente no artigo ilustra os resultados extraídos dos arquivos de saída acima da seguinte forma:

* A **Subfigura 3.a 50% de Domínios Aprimorados** apresenta os valores dos arquivos cuja modificação é descrita por Mod_8. Aqui as colunas `MEAN_PARETO_G` e `STDEV_PARETO_G` serviram de base para o cálculo do intervalo de confiança de 95%;

* A **Subfigura 3.b 75% de Domínios Aprimorados** apresenta os valores dos arquivos cuja modificação é descrita por Mod_9. Aqui as colunas `MEAN_PARETO_G` e `STDEV_PARETO_G` também serviram de base para o cálculo do intervalo de confiança de 95%.

A **Figura 4. Cenário 2: Média de Passos Geracionais para a Convergência** presente no artigo ilustra os resultados extraídos dos arquivos de saída acima da seguinte forma:

* A **Subfigura 4.a 50% de Domínios Aprimorados** apresenta os valores dos arquivos cuja modificação é descrita por Mod_8. Aqui a coluna `PARETO_SIZE` é utilizada;

* A **Subfigura 4.b 75% de Domínios Aprimorados** apresenta os valores dos arquivos cuja modificação é descrita por Mod_9. Aqui a coluna `PARETO_SIZE` também é utilizada.

### Reivindicação 3 (Cenário 3)
Para sua execução é necessário realizar o seguinte comando:
```
./run-tests-h3.sh
```
Os seguintes arquivos de saída, após a finalização da execução, serão movidos automaticamente para seus respectivos diretórios:
* Melhores Fronteiras `/35x11/h3/heritage_bests`:
    * 35x11-Mod_11-RELQUALITY(g_30000-p_100-h_30-bests-50%).csv;
    * 35x11-Mod_11-RELQUALITY(g_30000-p_100-h_30-bests-100%).csv;
    * 35x11-Mod_12-RELQUALITY(g_30000-p_100-h_30-bests-50%).csv;
    * 35x11-Mod_12-RELQUALITY(g_30000-p_100-h_30-bests-100%).csv;
    * 35x11-Mod_13-RELQUALITY(g_30000-p_100-h_30-bests-50%).csv;
    * 35x11-Mod_13-RELQUALITY(g_30000-p_100-h_30-bests-100%).csv.
* Fronteiras Aleatórias `/35x11/h3/heritage_random`:
    * 35x11-Mod_11-RELQUALITY(g_30000-p_100-h_30-random-50%).csv;
    * 35x11-Mod_11-RELQUALITY(g_30000-p_100-h_30-random-100%).csv;
    * 35x11-Mod_12-RELQUALITY(g_30000-p_100-h_30-random-50%).csv;
    * 35x11-Mod_12-RELQUALITY(g_30000-p_100-h_30-random-100%).csv;
    * 35x11-Mod_13-RELQUALITY(g_30000-p_100-h_30-random-50%).csv;
    * 35x11-Mod_13-RELQUALITY(g_30000-p_100-h_30-random-100%).csv.

O tempo médio de execução desse cenário é de 220 minutos.

A **Figura 5. Cenário 3: Média das Fronteiras Relativas** presente no artigo ilustra os resultados extraídos dos arquivos de saída acima da seguinte forma:

* A **Subfigura 5.a 4 Domínios Degradados** apresenta os valores dos arquivos cuja modificação é descrita por Mod_12. Aqui as colunas `MEAN_PARETO_G` e `STDEV_PARETO_G` serviram de base para o cálculo do intervalo de confiança de 95%;

* A **Subfigura 5.b 6 Domínios Degradados** apresenta os valores dos arquivos cuja modificação é descrita por Mod_13. Aqui as colunas `MEAN_PARETO_G` e `STDEV_PARETO_G` também serviram de base para o cálculo do intervalo de confiança de 95%.

### Observação 1
Os arquivos de saída já disponibilizados nos respectivos diretórios foram os utilizados para a elaboração dos gráficos. Ao reexecutar os *scripts* de teste, os arquivos originais serão substituídos.

### Observação 2
Os valores contidos nos arquivos de saída serão distintos a cada execução. Isso se deve à característica aleatória da abordagem genética considerada. No entanto, os valores não devem ser muito distantes dos já disponibilizados, pois os testes consideram um intervalo de confiança de 95%.


## Licença
Este projeto está licenciado sob a licença MIT. Consulte o arquivo [LICENSE](https://github.com/ViniGarcia/NFV-FLERAS/blob/GesemaExperiments/LICENSE) para mais detalhes.
