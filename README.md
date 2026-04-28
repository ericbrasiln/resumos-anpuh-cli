# Resumos-anpuh CLI

`resumosanpuh` é uma interface de linha de comando (CLI) para raspar, limpar e organizar os **resumos dos Simpósios Nacionais de História (ANPUH)**.

- **Anos suportados:** 2013, 2015, 2017, 2019, 2021\*, 2023 e 2025
- **Formatos de saída:** CSV (padrão) e JSON
- **Campos exportados:** `Ano`, `Evento`, `Cidade`, `ST`, `Coordenadores`, `Autor(es)/Instituições`, `Título`, `Resumo`

> **Aviso sobre 2021**
> O site do SNH **2021** encontra-se indisponível no momento dos testes. O CLI tenta acessar o endereço, registra a falha em arquivo `ERROR_<data>.txt`, informa o problema e segue com os demais anos. Trata-se de uma indisponibilidade do site, não necessariamente da ferramenta.

---

## Índice

- [Instalação](#instalação)
  - [Criar e ativar um ambiente virtual](#criar-e-ativar-um-ambiente-virtual)
  - [Instalar o pacote](#instalar-o-pacote)
- [Uso](#uso)
  - [Opções](#opções)
  - [Exemplos](#exemplos)
- [Formatos de saída](#formatos-de-saída)
- [Comportamento em caso de erro](#comportamento-em-caso-de-erro)
- [Campos do resultado](#campos-do-resultado)
- [Validação recente](#validação-recente)
- [Licença](#licença)

---

## Instalação

### Criar e ativar um ambiente virtual

Recomendado para evitar conflitos com pacotes do sistema:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows PowerShell/CMD
```

Para sair do ambiente virtual:

```bash
deactivate
```

### Instalar o pacote

Dentro da pasta do repositório:

```bash
pip install -e .
```

Isso instala o comando `resumosanpuh` e as dependências necessárias (`beautifulsoup4`, `lxml`, `pandas`, `requests`).

---

## Uso

Depois de instalado, rode o comando passando os anos com `-y/--years`.

```bash
resumosanpuh -y 2013 2015 2017 2019 2023 2025 -o resumos_anpuh.csv
```

### Opções

| Opção | Obrigatória | Padrão | Descrição |
|---|---:|---|---|
| `-y`, `--years` | Sim | — | Lista de anos a raspar. Ex.: `2013 2015 2017 2019 2021 2023 2025` |
| `-o`, `--output` | Não | `<AAAA-MM-DD_HH-MM-SS>.csv` | Nome do arquivo de saída |
| `-f`, `--format` | Não | `csv` | Formato de saída: `csv` ou `json` |
| `-v`, `--verbose` | Não | desativado | Mostra mensagens detalhadas |
| `-q`, `--quiet` | Não | desativado | Reduz a saída no terminal |

### Exemplos

CSV (padrão):

```bash
resumosanpuh -y 2019 2023 2025 -o resumos_19-23-25.csv
```

JSON:

```bash
resumosanpuh -y 2023 -f json -o resumos_2023.json
```

Vários anos em JSON:

```bash
resumosanpuh -y 2013 2015 2017 -f json -o resumos_13-15-17.json
```

Misturando anos com 2021:

```bash
resumosanpuh -y 2021 2023 2025 -o saida.csv -v
# Se 2021 estiver fora do ar, o CLI avisa, registra erro e continua com 2023/2025.
```

> Se você omitir a extensão em `-o`, ela é ajustada automaticamente conforme `-f` (`.csv` ou `.json`).

---

## Formatos de saída

### CSV

O CSV é o formato padrão e pode ser aberto em planilhas como LibreOffice, Excel ou analisado com pandas/R.

```bash
resumosanpuh -y 2025 -o resumos_2025.csv
```

### JSON

O JSON é exportado como lista de objetos (`orient='records'`), com indentação e preservação de acentos (`force_ascii=False`). É adequado para pipelines, APIs e integrações com ferramentas de análise textual.

```bash
resumosanpuh -y 2023 -f json -o resumos_2023.json
```

Exemplo simplificado:

```json
[
  {
    "Ano": 2023,
    "Evento": "XXXII",
    "Cidade": "São Luís",
    "ST": "ST 001...",
    "Coordenadores": "...",
    "Autor(es)/Instituições": "...",
    "Título": "...",
    "Resumo": "Texto completo do resumo..."
  }
]
```

---

## Comportamento em caso de erro

- O CLI tenta acessar o site do ano solicitado.
- Em caso de falha de rede, HTTP, DNS ou timeout, registra a ocorrência em `ERROR_<data>.txt`.
- A falha de um ano não interrompe a coleta dos demais anos.
- Em modo padrão ou `--verbose`, o CLI mostra avisos no terminal.
- Em modo `--quiet`, reduz as mensagens exibidas, mas continua registrando erros em arquivo.

---

## Campos do resultado

Cada registro contém:

```text
Ano, Evento, Cidade, ST, Coordenadores, Autor(es)/Instituições, Título, Resumo
```

Observações:

- `Ano`, `Evento` e `Cidade` são metadados do Simpósio Nacional de História.
- `ST` identifica o Simpósio Temático.
- `Coordenadores` registra os responsáveis pelo ST quando disponíveis.
- `Resumo` busca sempre o texto completo disponível no HTML da página.

---

## Validação recente

A ferramenta foi revisada e testada com os anos disponíveis entre 2013 e 2025. Resultado dos testes locais:

| Ano | Registros coletados | STs únicos | Situação |
|---:|---:|---:|---|
| 2013 | 2.678 | 112 | OK |
| 2015 | 2.770 | 113 | OK |
| 2017 | 2.802 | 102 | OK |
| 2019 | 3.240 | 113 | OK |
| 2021 | 0 | — | Site indisponível/DNS |
| 2023 | 2.372 | 86 | OK |
| 2025 | 3.512 | 126 | OK |

Notas da validação:

- Para 2023 e 2025, a ferramenta prioriza `resumoFull` quando disponível, evitando capturar apenas a prévia truncada (`resumoCurso`).
- Para 2013, foi identificado um ST sem programação disponível no site: `096. Imprensa ilustrada e jornalismo no Brasil do século XIX`; o comportamento esperado é registrar a ocorrência no arquivo de erro e seguir.
- Para 2015, há um registro cujo resumo disponível no site é apenas `.`; esse caso foi preservado como dado original.
- A saída JSON foi validada com 2023, gerando 2.372 registros em formato válido.

---

## Licença

MIT. Contribuições via issues e pull requests são bem-vindas.
