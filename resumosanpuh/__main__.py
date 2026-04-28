# creating a command line interface
import argparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import socket
import sys
import re
from urllib.parse import urljoin

dic = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
    )
}
now = datetime.now()
date = now.strftime("%Y-%m-%d_%H-%M-%S")
listaFinal = []

parser = argparse.ArgumentParser(
    description=(
        'Raspador dos resumos dos Simpósios Nacionais de História da Associação Nacional de História - Anpuh.\n'
        'Raspa os anos 2013, 2015, 2017, 2019, 2021, 2023 e 2025.\n'
        'Desenvolvido no âmbito do Laboratório de Humanidades Digitais da UFBA e parte do REDHBR.'
    )
)
parser.add_argument('-y','--years', nargs='+', metavar='', required=True,
                    help='Lista de anos a serem raspados. Ex.: 2013 2015 2017 2019 2021 2023 2025')
parser.add_argument('-o', '--output', metavar='',
                    help='Nome do arquivo de saída. Padrão: <AAAA-MM-DD_HH-MM-SS>.csv', default=f'{date}.csv')
parser.add_argument('-f', '--format', choices=['csv', 'json'], default='csv',
                    help='Formato de saída: csv (padrão) ou json')
parser.add_argument('-v', '--verbose', action='store_true', help='Ativar saída detalhada')
parser.add_argument('-q', '--quiet', action='store_true', help='Ativar saída silenciosa')
args = parser.parse_args()

def _log_info(msg: str):
    if not args.quiet:
        print(msg)

def _log_err(msg: str):
    if not args.quiet:
        print(msg, file=sys.stderr)
    with open(f'ERROR_{date}.txt', 'a', encoding='utf-8') as f:
        f.write(msg.rstrip() + '\n')

def cleanAbstract(abstract: str) -> str:
    """
    Limpa ruídos comuns nos resumos (2021/2023/2025):
    - quebra de linha; 'Resumo:'; 'RESUMO'; 'Ocultar'; 'Veja mais!'
    """
    if not abstract:
        return ''
    abstract = abstract.replace('\n', ' ')
    for bad in ['Resumo:', 'RESUMO', '\nOcultar', 'Ocultar', 'Veja mais!']:
        abstract = abstract.replace(bad, '')
    return abstract.strip()

def saveDF(listaFinal, output, fmt):
    df = pd.DataFrame(
        listaFinal,
        columns=['Ano', 'Evento', 'Cidade', 'ST', 'Coordenadores', 'Autor(es)/Instituições', 'Título', 'Resumo']
    )
    if fmt == 'json':
        if not output.endswith('.json'):
            output = output.rsplit('.', 1)[0] + '.json'
        df.to_json(output, orient='records', force_ascii=False, indent=2)
    else:  # csv
        if not output.endswith('.csv'):
            output = output.rsplit('.', 1)[0] + '.csv'
        df.to_csv(output, index=False)
    return output

def getAbstract(bs, year):
    """
    Extrai os trabalhos de uma página de ST.
    2013–2019: fluxo “antigo”
    2021/2023/2025: fluxo “moderno”, com diferenças:
        - 2023/2025: prioriza resumo completo em <div id="resumoFullXXXX">
        - fallback: resumoCursoXXXX ou style='display:none;font-size:11px;'
    """
    if bs is None:
        return
    year = int(year)

    # Metadados por ano
    if year == 2013:
        city, event = 'Natal', 'XXVII'
    if year == 2015:
        city, event = 'Florianópolis', 'XXVIII'
    if year == 2017:
        city, event = "Brasília", 'XXIX'
    if year == 2019:
        city, event = 'Recife', 'XXX'
    if year == 2021:
        city, event = 'Rio de Janeiro', 'XXXI'
    if year == 2023:
        city, event = 'São Luís', 'XXXII'
    if year == 2025:
        city, event = 'Belo Horizonte', 'XXXIII'

    # ----------- MODERNO: 2021/2023/2025 -----------
    if year in [2021, 2023, 2025]:
        # Em 2025, o wrapper 'col-xl-9 ...' pode não aparecer.
        # Estratégia: localizar o H3 do ST, subir até um container próximo e
        # achar a primeira tabela de trabalhos a partir dele.
        h3 = bs.find('h3', string=lambda s: s and s.strip().startswith('ST '))
        if not h3:
            _log_err(f'[PARSE] h3 do ST não encontrado (ano {year}).')
            return

        # Pega o container lógico onde ficam título, coordenadores e a tabela
        # (em 2025 o h3 está dentro de um div.container; em 2023 também)
        STInfos = h3.find_parent('div', class_='container') or h3.parent
        if not STInfos:
            _log_err(f'[PARSE] Container do ST (div.container) não encontrado (ano {year}).')
            return

        STtitle = h3.get_text(strip=True)
        coordinators_tag = STInfos.find('b')
        coordinators = coordinators_tag.get_text(strip=True) if coordinators_tag else 'Não foi definido'

        ST_table = h3.find_next('table') or STInfos.find('table')
        if not ST_table:
            _log_err(f'[PARSE] Tabela de trabalhos não encontrada (ano {year}, ST "{STtitle}").')
            return

        trs = ST_table.find_all('tr') or []
        for tr in trs:
            try:
                ul = tr.find('ul')
                li = ul.find('li') if ul else None
                if not li:
                    continue
                author = li.find('i').get_text(strip=True) if li.find('i') else ''
                title = li.find('b').get_text(strip=True) if li.find('b') else ''

                # Prioridade: resumoFull (texto completo) > resumoCurso (truncado)
                # 2023/2025: resumo com id="resumoFullXXXX" (completo)
                div_abs = li.find('div', id=re.compile(r'^resumoFull'))
                # 2025: fallback para resumoCurso se resumoFull não existir
                if not div_abs:
                    div_abs = li.find('div', id=re.compile(r'^resumoCurso'))
                # 2021/2023 antigo: resumo escondido via style
                if not div_abs:
                    div_abs = li.find(style='display:none;font-size:11px;')

                abstract = cleanAbstract(div_abs.get_text(' ', strip=True)) if div_abs else ''
                listaFinal.append([year, event, city, STtitle, coordinators, author, title, abstract])
            except Exception as e:
                _log_err(f'[PARSE] Erro ao extrair um trabalho (ano {year}, ST "{STtitle}"): {e}')
        return

    # ----------- ANTIGO: 2013–2019 -----------
    STContent = None
    if year in [2013, 2015]:
        STContent = bs.find(class_='content-interna')
    elif year in [2017, 2019]:
        STContent = bs.find(id='conteudo-spacer')
    if not STContent:
        _log_err(f'[PARSE] Container principal não encontrado (ano {year}).')
        return

    STInfos = STContent.find_all('table')
    if not STInfos:
        _log_err(f'[PARSE] Tabelas do ST não encontradas (ano {year}).')
        return

    STInfosGeral = STInfos[0]
    sttest = STInfosGeral.find_all('tr') or []
    if not sttest:
        _log_err(f'[PARSE] Linhas da tabela principal ausentes (ano {year}).')
        return

    h3 = sttest[0].find('h3') if sttest else None
    STtitle = h3.get_text(strip=True) if h3 else 'Título não encontrado'
    try:
        coordinators = sttest[1].find('b').get_text(strip=True) if len(sttest) > 1 else 'Não foi definido'
    except:
        coordinators = 'Não foi definido'

    programacao = STContent.find('h4')
    if programacao is None:
        if not args.quiet:
            print(f'Não foi encontrada nenhuma programação para o st {STtitle}')
        with open(f'ERROR_{date}.txt', 'a', encoding='utf-8') as f:
            f.write(f'Não foi encontrada nenhuma programação para o st {STtitle}\n')
        return

    stsTable = programacao.find_next_sibling()
    if not stsTable:
        _log_err(f'[PARSE] Tabela da programação inexistente (ano {year}, ST "{STtitle}").')
        return

    tds = stsTable.find_all('td') or []
    for paper in tds:
        try:
            author = paper.find('i').get_text(strip=True) if paper.find('i') else ''
            title = paper.find('b').get_text(strip=True) if paper.find('b') else ''
            node = paper.find(style='font-size:11px;') if year in [2013, 2015] else paper.find(style='display:none;font-size:11px;')
            abstract = cleanAbstract(node.get_text(' ', strip=True)) if node else ''
            listaFinal.append([year, event, city, STtitle, coordinators, author, title, abstract])
        except Exception as e:
            _log_err(f'[PARSE] Erro ao extrair um trabalho (ano {year}, ST "{STtitle}"): {e}')

def stList(bs, className, year):
    """
    Lista de STs do layout antigo (2013–2019).
    """
    if args.quiet is False:
        print(f'Raspando todos os resumos referentes ao ano {year}\nIsso pode demorar um pouco...')
    if bs is None:
        return

    STBoxe = bs.find('table', class_=className)
    if not STBoxe:
        _log_err(f'[PARSE] Tabela de STs não encontrada (ano {year}).')
        return

    STtrs = STBoxe.find_all('tr') or []
    for st in STtrs:
        tds = st.find_all('td')
        if not tds:
            continue
        td = tds[0]
        link_tag = td.find('h4') or td.find('h3')
        if not link_tag:
            continue
        a = link_tag.find('a')
        if not a or not a.get('href'):
            continue
        STlink = a['href']
        try:
            reqopen = Request(STlink, headers=dic)
            req = urlopen(reqopen, timeout=20.0)
            soup = BeautifulSoup(req.read(), 'html.parser')
            getAbstract(soup, year)
        except (HTTPError, URLError, socket.timeout) as e:
            _log_err(f'[ERRO] Falha ao acessar ST {STlink} (ano {year}): {e}')
        except Exception as e:
            _log_err(f'[ERRO] Exceção inesperada em {STlink} (ano {year}): {e}')

def STListHub(bs, year):
    """
    Lista de STs do HUB (layout moderno: 2021/2023/2025).
    2025 usa links ABSOLUTOS com parâmetro 'q=' antes de 'ID_ATIVIDADE', então
    evitamos regex estrito e aceitamos qualquer href que contenha 'atividade/view'.
    Também normalizamos links relativos e deduplicamos.
    """
    if bs is None:
        return
    if args.quiet is False:
        print(f'Raspando todos os resumos referentes ao ano {year}\nIsso pode demorar um pouco...')

    base = f'https://snh{year}.anpuh.org'
    anchors = bs.find_all('a')
    candidates = []

    def looks_like_st(href: str) -> bool:
        return bool(href) and ('atividade/view' in href.lower() or 'atividade/visualizar' in href.lower())

    for a in anchors:
        href = a.get('href')
        if looks_like_st(href):
            # normaliza
            href = href.strip()
            if href.startswith('//'):
                href = 'https:' + href
            if href.startswith('/'):
                href = urljoin(base, href)
            candidates.append(href)

    # dedupe preservando ordem
    seen, st_links = set(), []
    for u in candidates:
        if u and u not in seen:
            seen.add(u)
            st_links.append(u)

    if not st_links:
        _log_err(f'[PARSE] Nenhum link de ST encontrado no hub (ano {year}). Salvando snapshot do hub.')
        try:
            with open(f'HUB_{year}_{date}.html', 'w', encoding='utf-8') as f:
                f.write(bs.prettify())
        except Exception as e:
            _log_err(f'[DEBUG] Falha ao salvar snapshot do hub {year}: {e}')
        return

    for STlink in st_links:
        try:
            reqopen = Request(STlink, headers=dic)
            req = urlopen(reqopen, timeout=20.0)
            soup = BeautifulSoup(req.read(), 'html.parser')
            getAbstract(soup, year)
        except (HTTPError, URLError, socket.timeout) as e:
            _log_err(f'[ERRO] Falha ao acessar ST {STlink} (ano {year}): {e}')
        except Exception as e:
            _log_err(f'[ERRO] Exceção inesperada em {STlink} (ano {year}): {e}')

def request (url, dic, year):
    """
    Acessa a URL raiz do ano e despacha para o parser correto,
    mantendo a execução mesmo em caso de falha.
    """
    reqopen = Request(url, headers=dic)
    try:
        req = urlopen(reqopen, timeout=20.0)
        bs = BeautifulSoup(req.read(), 'html.parser')
    except (HTTPError, URLError, socket.timeout) as e:
        _log_err(f'[ERRO] Falha ao acessar {url} (ano {year}): {e}')
        _log_info(f'Aviso: não foi possível acessar o site do SNH {year}. Este ano será ignorado.')
        return
    except Exception as e:
        _log_err(f'[ERRO] Exceção inesperada ao acessar {url} (ano {year}): {e}')
        _log_info(f'Aviso: não foi possível acessar o site do SNH {year}. Este ano será ignorado.')
        return

    if year in ['2021', '2023', '2025']:
        STListHub(bs, year)
    else:
        stList(bs, 'txtConteudo', year)

def baseUrl(snhYears):
    for year in snhYears:
        if year == '2023':
            url = f'http://snh{year}.anpuh.org/atividade/hub/sts'
        elif year == '2025':
            url = f'https://snh{year}.anpuh.org/atividade/hub/sts'
        else:
            url = f'http://snh{year}.anpuh.org/simposio/public'
        if args.verbose:
            _log_info(f'[INFO] Acessando {url} (ano {year})')
        request(url, dic, year)

def main():
    if args.verbose:
        print(f'Iniciando raspagem dos resumos do(s) SNH {args.years}')
    elif args.quiet:
        print('Raspagem em modo silencioso')
    else:
        print(f'Iniciando raspagem dos resumos do(s) SNH {args.years}')
    baseUrl(args.years)
    final_file = saveDF(listaFinal, args.output, args.format)
    if not args.quiet:
        print(f'Concluído. Registros coletados: {len(listaFinal)}')
        print(f'Saída: {final_file}')

if __name__ == '__main__':
    main()
