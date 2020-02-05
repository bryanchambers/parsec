import json
import requests
import difflib
import csv



def parse_csv_value(line):
    i = line.find('"')
    text = line[i + 1:]

    j = text.find('"')
    value = text[:j].strip()

    remaining = text[j + 1:]
    return value, remaining



def get_tickers():
    tickers = {}

    for exchange in ['nyse', 'nasdaq']:
        url     = 'http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=' + exchange + '&render=download'
        file    = requests.get(url).text
        lines   = file.splitlines()

        for line in lines:
            ticker,  remaining = parse_csv_value(line)
            company, remaining = parse_csv_value(remaining)

            company = company.lower()

            if company not in tickers:
                tickers[company] = ticker.upper()

    with open('info/tickers.json', 'w') as file:
        json.dump(tickers, file)
        file.close()



def get_name_variations(n):
    v = { n: True }

    for punc in ['.', ',', '/']: 
        name = n.replace(punc, '')
        if name not in v: v[name] = True

    abv = {
        'inc':  'incorporated',
        'co':   'company',
        'corp': 'corporation',
        'ltd':  'limited',
        'llc': None,
        'lp':  None,
        'nv':  None
    }

    for a in abv:
        full = abv[a]
        base = [a, ' ' + a, a + '.']
        pre  = [',', ', ']

        find = []

        for b in base:
            find.append(b)
            for p in pre: find.append(p + b)

        repl = ['']
        if full: repl.append(full)

        for f in find:
            repl.append(f)
            repl.append(f + '.')

        for f in find: 
            for r in repl: 
                name = n.replace(f, r)
                if name not in v: v[name] = True

    return v



def parse_tickers():
    with open('info/tickers.json', 'r') as file:
        tickers = json.load(file)
        file.close()

    with open('info/companies.json', 'r') as file:
        companies = json.load(file)
        file.close()

    for cik in companies:
        name = companies[cik]['name'].lower()

        for variation in get_name_variations(name):
            if variation in tickers:
                companies[cik]['ticker'] = tickers[variation].upper()
                break

    with open('info/companies.json', 'w') as file:
        json.dump(companies, file)
        file.close()



get_tickers()
parse_tickers()