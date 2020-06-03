import json
from notify import email



def get_pe_score(pe):
    min = 10
    max = 100
    rng = max - min

    if pe < min: pe = min
    if pe > max: pe = max

    pe_frac = (pe - min) / rng
    return 100 - pe_frac * 100



def format_result(result):
    name    = result['name']
    ticker  = result['ticker']
    value   = str(round(result['value'], 1))
    pe      = str(round(result['pe'], 1))
    overall = str(round(result['overall'], 1))

    return '[' + ticker + '] ' + name + '\nOverall: ' + overall + ', Value: ' + value + ', PE: ' + pe



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

        result['overall'] = (result['value'] * 0.6) + (result['pe_score'] * 0.4) if 'pe_score' in result else 0
        if result['overall'] > 0: results.append(result)

results.sort(key=lambda x: x['overall'], reverse=True)



rows = []
for result in results:
    rows.append(format_result(result))



subject = 'Parsec Recommendations'
message = '\n\n'.join(rows)
email('bryches@gmail.com', subject, message)