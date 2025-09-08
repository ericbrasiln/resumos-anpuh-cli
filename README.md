# Resumos-anpuh CLI

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5252128.svg)](https://doi.org/10.5281/zenodo.5252128)

`resumosanpuh` é uma interface de linha de comando (CLI) em Python para raspar e organizar os **resumos dos Simpósios Nacionais de História** da [Associação Nacional de História — ANPUH](https://anpuh.org.br).

O programa raspa os resumos dos SNH 27, 28, 29, 30, 31 e 32 (2013, 2015, 2017, 2019, 2021 e 2023) e organiza a saída em **CSV (padrão)** ou **JSON**.

Foi construído a partir do script *Anpuh Scraper*, [DOI 10.5281/zenodo.5168720](https://doi.org/10.5281/zenodo.5168720), disponível [aqui](https://github.com/LABHDUFBA/anpuh-scraper).

Desenvolvido no âmbito do [Laboratório de Humanidades Digitais da UFBA](http://www.labhd.ufba.br/) e parte do [Repositório Digital das Humanidades (PT-BR) — REDHBR](https://labhdufba.github.io/redhbr/).

---

**A ferramenta foi desenvolvida apenas para pesquisas acadêmicas, sem fins lucrativos.**

---

O `resumosanpuh` foi pensado como ferramenta metodológica para pesquisas em humanidades digitais, fruto de reflexões e experiências de historiadores/as e sociólogos/as sobre o [desafio de fazer ciências humanas no mundo digital](http://bibliotecadigital.fgv.br/ojs/index.php/reh/article/view/79933). Os Simpósios Nacionais da ANPUH (bienais) reúnem debates centrais e seus anais constituem um repositório valioso de pesquisa.

---

## Índice

* [Instalação](#instalação)

  * [Bibliotecas e módulos](#bibliotecas-e-módulos)
* [Usos e opções](#usos-e-opções)
* [Comportamento em caso de erro](#comportamento-em-caso-de-erro)
* [Resultados](#resultados)
* [Licença](#licença)

---

## Instalação

Clone ou faça download do repositório e, no terminal, dentro da pasta `resumos-anpuh-cli`, execute:

```bash
sudo pip3 install -e .
```

Isso instalará o pacote e as dependências definidas em `setup.py` (BeautifulSoup, requests, lxml, pandas).

> Dica: você pode usar um ambiente virtual (`python3 -m venv .venv && source .venv/bin/activate`) antes do `pip install -e .`.

### Bibliotecas e módulos

* **urllib.request** — acesso a URLs.
* **bs4 / BeautifulSoup** — extração de dados de HTML/XML.
* **pandas** — manipulação/análise de dados tabulares.
* **lxml** — parser rápido e robusto para HTML/XML.

---

## Usos e opções

Após instalado, rode `resumosanpuh` passando os anos desejados com `-y/--years`.
Você pode escolher o **formato de saída** com `-f/--format` (`csv` ou `json`) e o **nome do arquivo** com `-o/--output`.

```bash
# CSV (padrão)
resumosanpuh -y 2013 2019 2023 -o resumos_2013-2019-2023.csv

# JSON
resumosanpuh -y 2013 2019 2023 -f json -o resumos_2013-2019-2023.json
```

Se você omitir a extensão em `-o`, ela é ajustada automaticamente conforme `-f`.

Ajuda completa:

```bash
resumosanpuh -h
```

**Opções principais:**

* `-y`, `--years` (obrigatório): anos a raspar (ex.: `2013 2015 2017 2019 2021 2023`)
* `-o`, `--output`: arquivo de saída (padrão: `<AAAA-MM-DD_HH-MM-SS>.csv`)
* `-f`, `--format`: `csv` (padrão) ou `json`
* `-v`, `--verbose`: saída detalhada
* `-q`, `--quiet`: saída silenciosa

---

## Comportamento em caso de erro

O CLI tenta acessar o site do ano solicitado e:

* Em caso de **falha de rede/HTTP/timeout**, registra a ocorrência em `ERROR_<data>.txt`, **mostra um aviso** (a menos que `--quiet`) e **segue para os outros anos** (execução resiliente).
* **2021**: o site pode estar **fora do ar**. Nessa situação, o CLI **tenta acessar**, **informa** que não foi possível e **pula 2021** automaticamente, sem interromper a coleta dos demais anos.

> Você pode usar `--verbose` para mensagens adicionais de diagnóstico, ou `--quiet` para minimizar a saída.

---

## Resultados

A ferramenta retorna um **arquivo CSV ou JSON** com os dados de todos os trabalhos aceitos nos Simpósios Temáticos dos anos informados.

Campos por registro:

```
Ano, Evento, Cidade, ST, Coordenadores, Autor(es)/Instituições, Título, Resumo
```

* **CSV**: abra em qualquer planilha (LibreOffice, Excel, etc.) ou processe com pandas/R.
* **JSON**: dicionário por registro (`orient='records'`), ideal para pipelines e integrações.

---

A ferramenta é mantida ativamente. Mudanças no site da ANPUH podem exigir ajustes — **issues e PRs são bem-vindos**.

---

## Licença

[MIT Licence](LICENSE)

---

Autor: [Eric Brasil](https://github.com/ericbrasiln) (IHLM-UNILAB e [LABHD-UFBA](http://labhd.ufba.br/))
