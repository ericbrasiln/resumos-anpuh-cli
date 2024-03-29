# Resumos-anpuh CLI

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5252128.svg)](https://doi.org/10.5281/zenodo.5252128)

`resumosanpuh` é uma interface de linha de comando (CLI) escrita em Python com objetivo de raspar e organizar os Resumos dos Simpósios Anuais da História da [Associação Nacional de História - Anpuh](https://anpuh.org.br).

O programa raspa todos os resumos dos SNH 27, 28, 29, 30, 31 e 32, respectivamente dos anos de 2013, 2015, 2017, 2019, 2021 e 2023 e organiza em um arquivo CSV.

Foi construído a partir do script _Anpuh Scraper_, [DOI 10.5281/zenodo.5168720](https://doi.org/10.5281/zenodo.5168720), dsiponível [aqui](https://github.com/LABHDUFBA/anpuh-scraper).

Desenvolvido no âmbito do [Laboratório de Humanidades Digitais da UFBA](http://www.labhd.ufba.br/) e parte do [Repositório Digital das Humanidades (PT-BR) - REDHBR](https://labhdufba.github.io/redhbr/).

___

**A ferramenta foi desenvolvida apenas para pesquisas acadêmicas, sem fins lucrativos.**
___

O `resumosanpuh` foi pensado como uma ferramenta metodológica da pesquisa em humanidades digitais. Sua criação é fruto das reflexões e experiências empíricas de historiadores e sociológos que têm enfrentado o [desafio de fazer ciências humanas no mundo digital](http://bibliotecadigital.fgv.br/ojs/index.php/reh/article/view/79933).

Defendemos a importância da apropriação, uso, desenvolvimento e aprimoramento de ferramentas digitais para as humanidades, assim como a urgência na sofisticação teórica, metodológica e epistemológica sobre as chamadas Humanidades Digitais.

É crescente o número de repositórios de fontes e dados on-line, assim como o acesso, busca, pesquisa e, muitas vezes, dependência de pesquisadores/as a eles.

Os Simpósios Nacionais da Anpuh, que acontecem bienalmente, têm reunido importantes reflexões sobre as mais variadas perspectivas historiográficas.

Por conseguinte, os anais de cada evento constituem um importante repositório para pesquisas nos mais variados campos de estudo.
___

## Índice

- [Resumos-anpuh CLI](#resumos-anpuh-cli)
  - [Índice](#índice)
  - [Instalação](#instalação)
    - [Bibliotecas e módulos](#bibliotecas-e-módulos)
  - [Usos e opções](#usos-e-opções)
  - [Resultados](#resultados)
  - [Licença](#licença)

---

## Instalação

Para executar o anpuh-scraper, vc precisa clonar ou fazer download do [repositório]() e salvar na pasta em que deseja que os resultados e seus respectivos arquivos sejam armazenados. 

A ferramenta consiste em uma interface de linha de comando (CLI) escrita em [Python 3](https://www.python.org/). 

Para informações de como instalar o Python em seu sistema operacional, veja a lição [Introdução e instalação do Python](https://programminghistorian.org/pt/licoes/introducao-instalacao-python) no Programming Historian.

Abra o terminal e mude seu caminho até a pasta `resumos-anpuh-cli` e execute o comando:

```
sudo pip3 install -e .
```

OBS: Se você não possui o pip instalado basta executar no terminal `sudo apt install python3-pip` em sistemas operacionais baseados no Ubuntu. Para instruções de instalação no Windows ver essa lição do [Programming Historian](https://programminghistorian.org/es/lecciones/instalar-modulos-python-pip#instrucciones-para-windows).

As bibliotecas e módulos, assim como o pacote, serão instalados automaticamente.

### Bibliotecas e módulos

- **urllib.requests**: módulo do Python que ajuda a acessar urls.
[Saiba mais.](https://docs.python.org/pt-br/3/library/urllib.request.htmll)
- **bs4**: [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) é uma biblioteca Python para extrair
 dados de arquivos HTML e XML.
- **pandas**: [Pandas](https://pandas.pydata.org/) é uma biblioteca escrita em Python para manipulação e análise de dados. 

---

## Usos e opções

Após a instalação, para executar a ferramenta basta abrir o terminal e digitar  `resumosanpuh` seguido de `-y` ou `--years` e passar os anos que deseja raspar como parâmetro `2013 2015 2017 2019 2021`. 

Opcionalmente é possível definir o nome do arquivo csv final acrescentando `-o` ou `--output` seguido de `<nome_do_arquivo>.csv`. Caso essa opção não seja definida o título do arquivo será `<AAAA-MM-DD_HH-MM-SS>.csv`

```bash
resumosanpuh -y 2013 2019 -o resumos_2013-2019.csv
```

Também é possível utilizar a opção `-h` ou `--help` para ver a ajuda completa.

```bash
resumosanpuh -h

usage: resumosanpuh [-h] -y  [...] [-o] [-v] [-q]

Raspador dos resumos dos Simpósios Nacionais de História da Associação
Nacional de História - Anpuh. O programa raspa todos os resumos dos SNH 27,
28, 29, 30, 31 e 32, respectivamente dos anos de 2013, 2015, 2017, 2019, 2021
e 2023. Desenvolvido no âmbito do Laboratório de Humanidades Digitais da UFBA
e parte do Repositório Digital das Humanidades (PT-BR) - REDHBR.

options:
  -h, --help            show this help message and exit
  -y  [ ...], --years  [ ...]
                        Lista de anos a serem raspados. Exemplo: 2013 2015
                        2017 2019 2021 2023. Essa opção é obrigatória.
  -o , --output         Nome do arquivo de saída no formato .csv. Se essa
                        opção não for definida, o título do arquivo será
                        `<AAAA-MM-DD_HH-MM-SS>.csv
  -v, --verbose         Ativar saída detalhada
  -q, --quiet           Ativar saída silenciosa

```

![image](https://user-images.githubusercontent.com/58128421/130711906-cdb0ffea-fbd1-4699-885e-1e1bcf00ad9d.png)

---

## Resultados

A ferramente retorna para o usuário **um CSV (*comma-separated values*) com os dados de todos os trabalhos aceitos nos Simpósio Temáticos dos SNH 27, 28, 29, 30, 31 e 32**.

O CSV contém as seguintes variáveis para cada resumo:

`Ano, Evento, Cidade, ST, Coordenadores, Autor(es)/Instituições, Título, Resumo`

Esse arquivo pode ser aberto como uma planilha e trabalhado em banco de dados.

Contando o número de linhas e de linhas por ano, com pandas, temos o seguinte resultado:

![image](https://user-images.githubusercontent.com/58128421/130712111-f8654c2c-0d81-4b65-89ba-b5e567f96fea.png)

---

A ferramenta está funcionando perfeitamente. Qualquer alteração no site ou nos resultados percebida pelos usuários ou sugestões de aprimoramento são bem vindas.

---

## Licença

[MIT Licence](LICENSE)

---

Autor: [Eric Brasil](https://github.com/ericbrasiln) (IHLM-UNILAB e [LABHD-UFBA](http://labhd.ufba.br/))
