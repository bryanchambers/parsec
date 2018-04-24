import requests
import db

dbc    = db.dbConnect('localhost', 'root', 'atlas', 'parsec')
cursor = db.getCursor(dbc)





def get_pe_ratio(ticker):
	page = requests.get('http://www.nasdaq.com/symbol/' + ticker).content
	
	i = page.find('P/E Ratio')
	if i < 0: 
		return False
	snip = page[i:i + 200]
	
	i = snip.find('.')
	if i >= 0:
		snip = snip[i - 3:i + 3]

	parsed = []
	for char in snip:
		if char.isdigit() or char == '.':
			parsed.append(char)
	snip = ''.join(parsed).strip()
	
	if len(snip) == 0:
		return False
	pe = float(snip)
	
	if pe > 10000: pe = 10000
	if pe <     0: pe = 0
	return int(pe)





def get_pe_score(pe):
	pe_max = 50
	pe_min = 5

	if not pe:
		return False

	scale = 100 / float(pe_max - pe_min)
	score = 100 - (((float(pe) / 10) * scale) - (pe_min * scale))

	if score > 100: score = 100
	if score <   0: score = 0
	return int(score)





print('\033[2J\033[1;1H')
print('### PARSEC QUOTES ###')

companies = db.get_listed_companies(dbc, cursor)

if companies['success']:
	print('Found ' + str(len(companies['data'])) + ' companies with tickers')
	for company in companies['data']:
		pe_ratio = get_pe_ratio(company['ticker'])
		pe_score = get_pe_score(pe_ratio)
		db.save_pe(dbc, cursor, company['cik'], pe_ratio, pe_score)
