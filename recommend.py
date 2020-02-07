import json



def get_pe_score(pe):
    min = 1
    max = 50
    rng = max - min

    if pe < min: pe = min
    if pe > max: pe = max

    pe_frac = (pe - min) / rng
    return 100 - pe_frac * 100



def print_result(result):
    name    = result['name']
    ticker  = result['ticker'].ljust(5)
    value   = str(round(result['value'], 1)).rjust(5)
    pe      = str(round(result['pe'], 1)).rjust(5)
    overall = str(round(result['overall'], 1)).rjust(5)

    print('| ' + ' | '.join([value, pe, overall, ticker, name]))



with open('info/companies.json', 'r') as file:
    companies = json.load(file)
    file.close()

with open('scores/value-scores.json', 'r') as file:
    scores = json.load(file)
    file.close()

results = []

for cik in scores:
    if cik in companies:
        result = companies[cik]
        result['cik']   = cik
        result['value'] = scores[cik]
        if 'pe' in result: result['pe_score'] = get_pe_score(result['pe'])

        result['overall'] = (result['value'] + result['pe_score']) / 2 if 'pe_score' in result else 0
        if result['overall'] > 0: results.append(result)

results.sort(key=lambda x: x['overall'], reverse=True)

print('')
print('-' * 80)
print('| ' + ' | '.join(['Value', '   PE', 'Final', 'Tick ', 'Name']))
print('-' * 80)
for result in results: print_result(result)
print('-' * 80)
