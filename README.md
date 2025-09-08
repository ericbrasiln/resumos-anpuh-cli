# Resumos-anpuh CLI

`resumosanpuh` é uma interface de linha de comando (CLI) para raspar e organizar os **resumos dos Simpósios Nacionais de História (ANPUH)**.

* **Anos suportados:** 2013, 2015, 2017, 2019, 2021\*, 2023 e **2025**
* **Formatos de saída:** CSV (padrão) e JSON

> **Aviso sobre 2021**
> O site do SNH **2021** encontra-se **fora do ar**. O CLI tenta acessar e, caso falhe, **informa o problema e segue** com os demais anos. Trata-se de uma **indisponibilidade do site**, não da ferramenta.

---

## Índice

* [Instalação](#instalação)

  * [Criar e ativar um ambiente virtual (recomendado)](#criar-e-ativar-um-ambiente-virtual-recomendado)
  * [Instalar o pacote](#instalar-o-pacote)
* [Uso](#uso)

  * [Opções](#opções)
  * [Exemplos](#exemplos)
* [Comportamento em caso de erro](#comportamento-em-caso-de-erro)
* [Campos do resultado](#campos-do-resultado)
* [Licença](#licença)

---

## Instalação

### Criar e ativar um ambiente virtual (recomendado)

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows (PowerShell/CMD)
```

> Para sair do ambiente virtual depois: `deactivate`

### Instalar o pacote

Dentro da pasta do repositório:

```bash
pip install -e .
```

Isso instalará o CLI `resumosanpuh` e as dependências (BeautifulSoup, lxml, pandas etc.).

---

## Uso

Depois de instalado, rode o comando passando os anos com `-y/--years`.
Você pode escolher o **formato** com `-f/--format` (`csv` ou `json`) e o **nome do arquivo** com `-o/--output`.

### Opções

* `-y`, `--years` (obrigatório): anos a raspar, por exemplo `2013 2015 2017 2019 2021 2023 2025`
* `-o`, `--output`: nome do arquivo de saída (padrão: `<AAAA-MM-DD_HH-MM-SS>.csv`)
* `-f`, `--format`: `csv` (padrão) ou `json`
* `-v`, `--verbose`: saída detalhada
* `-q`, `--quiet`: saída silenciosa

### Exemplos

CSV (padrão):

```bash
resumosanpuh -y 2019 2023 2025 -o resumos_19-23-25.csv
```

JSON:

```bash
resumosanpuh -y 2013 2015 2017 -f json -o resumos_13-15-17.json
```

Misturando anos (com 2021):

```bash
resumosanpuh -y 2021 2023 2025 -o saida.csv -v
# Se 2021 estiver fora do ar, o CLI avisa e continua com 2023/2025.
```

> Se você omitir a extensão em `-o`, ela é ajustada automaticamente com base em `-f`.

---

## Comportamento em caso de erro

* O CLI tenta acessar o site do ano solicitado.
  Em **falha de rede/HTTP/timeout**, registra a ocorrência em `ERROR_<data>.txt`, **mostra um aviso** (a menos que `--quiet`) e **continua** com os demais anos.
* **2021:** como o site pode estar **indisponível**, a ferramenta **tenta**, **avisa** se não conseguir e **pula** este ano sem interromper a execução.

---

## Campos do resultado

Cada registro possui:

```
Ano, Evento, Cidade, ST, Coordenadores, Autor(es)/Instituições, Título, Resumo
```

* **CSV:** abra em planilhas (LibreOffice/Excel) ou consuma com pandas/R.
* **JSON:** `orient='records'`, ideal para pipelines e integrações.

---

## Licença

MIT. Contribuições (issues/PRs) são bem-vindas!
