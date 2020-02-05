import requests
import datetime
import json



def get_pe_batch(ticker_batch):
    base_url = 'https://api.iextrading.com/1.0/stock/market/batch?symbols='
    tickers  = ','.join(ticker_batch)
    quotes   = requests.get(base_url + tickers + '&types=quote').json()

    out = {}

    for ticker in quotes:
        quote = quotes[ticker]['quote']

        if 'peRatio' in quote:
            pe = quote['peRatio']
            if pe and pe > 0: out[ticker] = quote['peRatio']

    return out



def get_ticker_batches():
    with open('info/companies.json', 'r') as file:
        companies = json.load(file)
        file.close()

    out   = []
    batch = []

    for cik in companies:
        if 'ticker' in companies[cik]:
            batch.append(companies[cik]['ticker'])
            
            if len(batch) > 100:
                out.append(batch)
                batch = []

    return out



def get_pe_ratios():
    pe = {}

    for batch in get_ticker_batches():
        pe = { **pe, **get_pe_batch(batch) }

    with open('info/companies.json', 'r') as file:
        companies = json.load(file)
        file.close()
    
    for cik in companies:
        if 'ticker' in companies[cik]:

            ticker = companies[cik]['ticker']
            if ticker in pe: companies[cik]['pe'] = pe[ticker]
    
    with open('info/companies.json', 'w') as file:
        json.dump(companies, file)
        file.close()



def get_pe_score(pe):
    min = 1
    max = 50
    rng = max - min

    if pe < min: pe = min
    if pe > max: pe = max

    pe_frac = (pe - min) / rng

    return 100 - pe_frac * 100



get_pe_ratios()