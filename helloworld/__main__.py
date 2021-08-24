# creating a comand line interface
import argparse
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


dic = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
now = datetime.now()
date = now.strftime("%Y-%m-%d_%H-%M-%S")
listaFinal = []

parser = argparse.ArgumentParser(description='Raspador dos resumos dos Simpósios Nacionais de História da Associação Nacional de História - Anpuh.\n'
                                             'O programa raspa todos os resumos dos SNH 27, 28, 29, 30 e 31, respectivamente dos anos de 2013, 2015, 2017, 2019 e 2021.\n'
                                             'Desenvolvido no âmbito do Laboratório de Humanidades Digitais da UFBA e parte do Repositório Digital das Humanidades (PT-BR) - REDHBR.')
parser.add_argument('-y','--years', nargs='+', metavar='', required=True, help='Lista de anos a serem raspados. Exemplo: 2013 2015 2017 2019 2021. Essa opção é obrigatória.')
parser.add_argument('-o', '--output', metavar='', help='Nome do arquivo de saída no formato .csv. Se essa opção não for definida, o título do arquivo será `<AAAA-MM-DD_HH-MM-SS>.csv', default=f'{date}.csv')
args = parser.parse_args()

def cleanAbstract(abstract):
    '''
    Função que limpa o resumo do evento
    '''
    abstract = abstract.replace('\n', ' ')
    abstract = abstract.replace('Resumo:','')
    abstract = abstract.replace('\nOcultar','')
    abstract = abstract.replace('RESUMO','')
    return abstract

def saveDF(listaFinal, output):
    '''
    Função que salva o DataFrame com os resumos dos simpósios Nacionais de História da Anpuh
    '''
    df = pd.DataFrame(listaFinal, columns=['Ano', 'Evento', 'Cidade', 'ST', 'Coordenadores', 'Autor(es)/Instituições', 'Título', 'Resumo'])
    df.to_csv(f'{output}')

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
    if year in [2013, 2015]:
        STContent = bs.find(class_='content-interna')
    elif year in [2017, 2019]:
        STContent = bs.find(id='conteudo-spacer')
    else:
        STContent = bs.find(class_='col-xl-9 col-lg-8 pl-4 pr-4 pt-3 pb-3 w-100')
    if year == 2021:
        STInfos = STContent.find(class_='container')
        STtitle = STInfos.find('h3').text
        coordinators = STInfos.find('b').text
        ST_table = STInfos.find('table')
        sts = ST_table.find_all('tr')
        for paper in sts:
            author = paper.find('i').text
            print(author)
            title = paper.find('b').text 
            abstract = paper.find(style='display:none;font-size:11px;').text.strip()
            abstract = cleanAbstract(abstract)
            listaInterna = [year, event, city, STtitle, coordinators, author, title, abstract]
            listaFinal.append(listaInterna)
    else:
        STInfos = STContent.find_all('table')
        STInfosGeral = STInfos[0]
        sttest = STInfosGeral.find_all('tr')
        STtitle = sttest[0].find('h3').text
        try:
            coordinators = sttest[1].find('b').text
        except:
            coordinators = 'Não foi definido'
        #finds 'h4' in STContent
        programacao = STContent.find('h4')
        if programacao is None:
            print(f'Não foi encontrada nenhuma programação para o st {STtitle}')
            #creates a txt file with the error and saves it
            with open(f'ERROR_{date}.txt', 'a') as f:
                f.write(f'Não foi encontrada nenhuma programação para o st {STtitle}\n')
                f.close()
        else:
            stsTable = programacao.find_next_sibling()
            sts = stsTable.find_all('td')
            for paper in sts:
                author = paper.find('i').text
                print(author)
                title = paper.find('b').text
                if year in [2013, 2015]:
                    abstract = paper.find(style='font-size:11px;').text.strip()
                    abstract = cleanAbstract(abstract)
                else: 
                    abstract = paper.find(style='display:none;font-size:11px;').text.strip()
                    abstract = cleanAbstract(abstract)
                listaInterna = [year, event, city, STtitle, coordinators, author, title, abstract]
                listaFinal.append(listaInterna)

def stList(bs, className, year):
    '''
    Função que raspa a lista de Simpósios Temáticos
    '''
    print(f'Raspando todos os resumos referentes ao ano {year}\n'
          'Isso pode demorar um pouco...')
    STBoxe = bs.find('table', class_= className)
    STtrs = STBoxe.find_all('tr')
    #find all trs in STtrs
    for st in STtrs:
        STInfos = st.find_all('td')
        STInfos = STInfos[0]
        if STInfos.find('h4'):
            STtitle = STInfos.find('h4')
            STlink = STtitle.find('a')['href']
            reqopen = Request(STlink)
            req = urlopen(reqopen)
            soup = BeautifulSoup(req.read(), 'lxml')
            getAbstract(soup, year)
        elif STInfos.find('h3'):
            STtitle = STInfos.find('h3')
            STlink = STtitle.find('a')['href']
            reqopen = Request(STlink)
            req = urlopen(reqopen)
            soup = BeautifulSoup(req.read(), 'lxml')
            getAbstract(soup, year)
        else:
            pass

def request (url, dic, year):
    '''
    Função que acessa a URL com urlopen e faz o parse do html com BeautifulSoup
    '''
    reqopen = Request(url, headers=dic)
    req = urlopen(reqopen)
    bs = BeautifulSoup(req.read(), 'lxml')
    stList(bs, 'txtConteudo', year)

def baseUrl(snhYears):
    '''
    Função para definir a URL base para a raspagem dos resumos
    '''
    for year in snhYears:
        url = f'http://snh{year}.anpuh.org/simposio/public'
        request(url,dic, year)

def main():
    baseUrl(args.years)
    saveDF(listaFinal, args.output)

if __name__ == '__main__':
    main()
