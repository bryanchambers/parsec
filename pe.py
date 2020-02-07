import requests
import datetime
import json



def get_api_info():
    with open('iex.json', 'r') as file:
        api = json.load(file)

    return api



def get_pe_batch(ticker_batch):
    base_url = api['base'] + '?symbols='
    tickers  = ','.join(ticker_batch)
    types    = '&types=quote'
    token    = '&token=' + api['token']
    response = requests.get(base_url + tickers + types + token)
    quotes   = response.json()

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


api = get_api_info()
get_pe_ratios()