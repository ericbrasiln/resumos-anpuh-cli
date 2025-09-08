# creating a command line interface
import argparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import socket
import sys

dic = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
now = datetime.now()
date = now.strftime("%Y-%m-%d_%H-%M-%S")
listaFinal = []

parser = argparse.ArgumentParser(description='Raspador dos resumos dos Simpósios Nacionais de História da Associação Nacional de História - Anpuh.\n'
                                             'O programa raspa todos os resumos dos SNH 27, 28, 29, 30, 31 e 32, respectivamente dos anos de 2013, 2015, 2017, 2019, 2021 e 2023.\n'
                                             'Desenvolvido no âmbito do Laboratório de Humanidades Digitais da UFBA e parte do Repositório Digital das Humanidades (PT-BR) - REDHBR.')
parser.add_argument('-y','--years', nargs='+', metavar='', required=True, help='Lista de anos a serem raspados. Exemplo: 2013 2015 2017 2019 2021 2023. Essa opção é obrigatória.')
parser.add_argument('-o', '--output', metavar='', help='Nome do arquivo de saída no formato .csv. Se essa opção não for definida, o título do arquivo será <AAAA-MM-DD_HH-MM-SS>.csv', default=f'{date}.csv')
parser.add_argument('-v', '--verbose', action='store_true', help='Ativar saída detalhada')
parser.add_argument('-q', '--quiet', action='store_true', help='Ativar saída silenciosa')
parser.add_argument(
    '-f', '--format', choices=['csv', 'json'], default='csv',
    help='Formato de saída: csv (padrão) ou json'
)
args = parser.parse_args()

def _log_info(msg: str):
    if not args.quiet:
        print(msg)

def _log_err(msg: str):
    if not args.quiet:
        print(msg, file=sys.stderr)
    with open(f'ERROR_{date}.txt', 'a', encoding='utf-8') as f:
        f.write(msg.rstrip() + '\n')

def cleanAbstract(abstract):
    '''
    Função que limpa o resumo do evento
    '''
    abstract = abstract.replace('\n', ' ')
    abstract = abstract.replace('Resumo:','')
    abstract = abstract.replace('\nOcultar','')
    abstract = abstract.replace('RESUMO','')
    return abstract.strip()

def saveDF(listaFinal, output, fmt):
    '''
    Função que salva o DataFrame com os resumos dos simpósios Nacionais de História da Anpuh
    '''
    df = pd.DataFrame(listaFinal, columns=['Ano', 'Evento', 'Cidade', 'ST', 'Coordenadores', 'Autor(es)/Instituições', 'Título', 'Resumo'])
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
    '''
    Função que raspa os resumos de cada simpósio Nacional de História
    '''
    year = int(year)
    if year == 2013:
        city = 'Natal'
        event = 'XXVII'
    if year == 2015:
        city = 'Florianópolis'
        event = 'XXVIII'
    if year == 2017:
        city = "Brasília"
        event = 'XXIX'
    if year == 2019:
        city = 'Recife'
        event = 'XXX'
    if year == 2021:
        city = 'Rio de Janeiro'
        event = 'XXXI'
    if year == 2023:
        city = 'São Luís'
        event = 'XXXII'

    if year in [2013, 2015]:
        STContent = bs.find(class_='content-interna')
    elif year in [2017, 2019]:
        STContent = bs.find(id='conteudo-spacer')
    else:
        STContent = bs.find(class_='col-xl-9 col-lg-8 pl-4 pr-4 pt-3 pb-3 w-100')

    if not STContent:
        _log_err(f'[PARSE] Container principal não encontrado (ano {year}).')
        return

    if year == 2021 or year == 2023:
        STInfos = STContent.find(class_='container')
        if not STInfos:
            _log_err(f'[PARSE] .container não encontrado (ano {year}).')
            return
        h3 = STInfos.find('h3')
        b = STInfos.find('b')
        ST_table = STInfos.find('table')
        if not (h3 and b and ST_table):
            _log_err(f'[PARSE] h3/b/table ausentes no ST (ano {year}).')
            return

        STtitle = h3.text.strip()
        coordinators = b.text.strip()
        sts = ST_table.find_all('tr') or []
        for paper in sts:
            try:
                li = paper.find('ul').find('li')
                if not li:
                    continue
                author = li.find('i').text.strip() if li.find('i') else ''
                title = li.find('b').text.strip() if li.find('b') else ''
                absnode = li.find(style='display:none;font-size:11px;')
                abstract = cleanAbstract(absnode.text) if absnode else ''
                listaInterna = [year, event, city, STtitle, coordinators, author, title, abstract]
                listaFinal.append(listaInterna)
            except Exception as e:
                _log_err(f'[PARSE] Erro ao extrair um trabalho (ano {year}, ST "{STtitle}"): {e}')
    else:
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
        STtitle = h3.text.strip() if h3 else 'Título não encontrado'
        try:
            coordinators = sttest[1].find('b').text.strip() if len(sttest) > 1 else 'Não foi definido'
        except:
            coordinators = 'Não foi definido'
        #finds 'h4' in STContent
        programacao = STContent.find('h4')
        if programacao is None:
            if not args.quiet:
                print(f'Não foi encontrada nenhuma programação para o st {STtitle}')
            with open(f'ERROR_{date}.txt', 'a', encoding='utf-8') as f:
                f.write(f'Não foi encontrada nenhuma programação para o st {STtitle}\n')
        else:
            stsTable = programacao.find_next_sibling()
            if not stsTable:
                _log_err(f'[PARSE] Tabela da programação inexistente (ano {year}, ST "{STtitle}").')
                return
            sts = stsTable.find_all('td') or []
            for paper in sts:
                try:
                    author = paper.find('i').text.strip() if paper.find('i') else ''
                    title = paper.find('b').text.strip() if paper.find('b') else ''
                    if year in [2013, 2015]:
                        node = paper.find(style='font-size:11px;')
                    else:
                        node = paper.find(style='display:none;font-size:11px;')
                    abstract = cleanAbstract(node.text) if node else ''
                    listaInterna = [year, event, city, STtitle, coordinators, author, title, abstract]
                    listaFinal.append(listaInterna)
                except Exception as e:
                    _log_err(f'[PARSE] Erro ao extrair um trabalho (ano {year}, ST "{STtitle}"): {e}')

def stList(bs, className, year):
    '''
    Função que raspa a lista de Simpósios Temáticos (layout antigo)
    '''
    if args.quiet == False:
        print(f'Raspando todos os resumos referentes ao ano {year}\n'
              'Isso pode demorar um pouco...')
    if bs is None:
        return
    STBoxe = bs.find('table', class_= className)
    if not STBoxe:
        _log_err(f'[PARSE] Tabela de STs não encontrada (ano {year}).')
        return
    STtrs = STBoxe.find_all('tr') or []
    for st in STtrs:
        STInfos = st.find_all('td')
        if not STInfos:
            continue
        STInfos = STInfos[0]
        link_tag = STInfos.find('h4') or STInfos.find('h3')
        if not link_tag:
            continue
        a = link_tag.find('a')
        if not a or not a.get('href'):
            continue
        STlink = a['href']
        try:
            reqopen = Request(STlink, headers=dic)
            req = urlopen(reqopen, timeout=20.0)
            soup = BeautifulSoup(req.read(), 'html.parser' )
            getAbstract(soup, year)
        except (HTTPError, URLError, socket.timeout) as e:
            _log_err(f'[ERRO] Falha ao acessar ST {STlink} (ano {year}): {e}')
        except Exception as e:
            _log_err(f'[ERRO] Exceção inesperada em {STlink} (ano {year}): {e}')

# função para ano de 20203
def STList2023(bs, className, year):
    '''
    Função que raspa a lista de Simpósios Temáticos (layout moderno 2021/2023)
    '''
    if args.quiet is False:
        print(f'Raspando todos os resumos referentes ao ano {year}\n'
              'Isso pode demorar um pouco...')
    if bs is None:
        return
    STBoxe = bs.find('div', class_= className)
    if not STBoxe:
        _log_err(f'[PARSE] Box principal não encontrado (ano {year}).')
        return
    STBoxe = STBoxe.find('div', class_='container')
    if not STBoxe:
        _log_err(f'[PARSE] .container não encontrado (ano {year}).')
        return
    STBoxe = STBoxe.find('div', class_='first mt-4')
    if not STBoxe:
        _log_err(f'[PARSE] .first mt-4 não encontrado (ano {year}).')
        return
    STtrs = STBoxe.find_all('div', class_='first') or []
    for st in STtrs:
        STInfos = st.find('h5')
        a = STInfos.find('a') if STInfos else None
        STlink = a['href'] if a and a.get('href') else None
        if not STlink:
            continue
        try:
            reqopen = Request(STlink, headers=dic)
            req = urlopen(reqopen, timeout=20.0)
            soup = BeautifulSoup(req.read(), 'html.parser' )
            getAbstract(soup, year)
        except (HTTPError, URLError, socket.timeout) as e:
            _log_err(f'[ERRO] Falha ao acessar ST {STlink} (ano {year}): {e}')
        except Exception as e:
            _log_err(f'[ERRO] Exceção inesperada em {STlink} (ano {year}): {e}')

def request (url, dic, year):
    '''
    Função que acessa a URL com urlopen e faz o parse do html com BeautifulSoup
    (tenta, avisa em caso de falha, e continua para os demais anos)
    '''
    reqopen = Request(url, headers=dic)
    try:
        req = urlopen(reqopen, timeout=20.0)
        bs = BeautifulSoup(req.read(), 'html.parser' )
    except (HTTPError, URLError, socket.timeout) as e:
        _log_err(f'[ERRO] Falha ao acessar {url} (ano {year}): {e}')
        _log_info(f'Aviso: não foi possível acessar o site do SNH {year}. Este ano será ignorado.')
        return
    except Exception as e:
        _log_err(f'[ERRO] Exceção inesperada ao acessar {url} (ano {year}): {e}')
        _log_info(f'Aviso: não foi possível acessar o site do SNH {year}. Este ano será ignorado.')
        return

    if year == '2023':
        STList2023(bs, 'col-xl-9 col-lg-8 pl-4 pr-4 pt-3 pb-3 w-100', year)
    else:
        # Mantido exatamente como antes: 2021 continua passando por stList
        stList(bs, 'txtConteudo', year)

def baseUrl(snhYears):
    '''
    Função para definir a URL base para a raspagem dos resumos
    (mantém as URLs originais; apenas adiciona logs/erros)
    '''
    for year in snhYears:
        if year == '2023':
            url = f'http://snh{year}.anpuh.org/atividade/hub/sts'
        else:
            url = f'http://snh{year}.anpuh.org/simposio/public'
        if args.verbose:
            _log_info(f'[INFO] Acessando {url} (ano {year})')
        request(url,dic, year)

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
