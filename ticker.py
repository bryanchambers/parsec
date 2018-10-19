import requests
import db
import datetime
import sys

dbc    = db.dbConnect('localhost', 'root', 'atlas', 'parsec')
cursor = db.getCursor(dbc)





def get_tickers(exchange):
	if exchange in ['nyse', 'nasdaq']:
		url     = 'http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=' + exchange + '&render=download'
		file    = requests.get(url).content
		lines   = file.splitlines()
		tickers = {}
		
		for line in lines:
			data = line.split(',')
			ticker  = data[0].replace('"', '').strip().upper()
			company = data[1].replace('"', '').strip().lower()
			
			if '.' in ticker:
				ticker = ticker[:ticker.find('.')]
			
			if '^' not in ticker and len(ticker) > 0:
				if company not in tickers:
					tickers[company] = str(ticker)
		return tickers
	else:
		return False





def get_all_tickers(exchanges):
	all_tickers = {}
	for exchange in exchanges:
		tickers = get_tickers(exchange)
		if tickers and len(tickers) > 0:
			all_tickers.update(tickers)
	if len(all_tickers) > 0:
		return all_tickers
	else:
		return False





def replace_common_strings(name):
	replacements = [
		{'old': 'the',    'new': ''},
		{'old': '-',      'new': ' '},
		{'old': '&#39;',  'new': ''},
		{'old': 'co.',    'new': 'co'},
		{'old': 'inc.',   'new': 'inc'},
		{'old': 'u.s.a.', 'new': 'usa'},
		{'old': 'u.s. ',  'new': 'us '},
		{'old': '?',      'new': ''},
		{'old': '!',      'new': ''},
		{'old': ' & ',    'new': ' and '},
		{'old': "'",      'new': ''},
		{'old': 'hldgs',  'new': 'holdings'},
	]
	for replacement in replacements:
		name = name.replace(replacement['old'], replacement['new'])
	return name





def common_name_variations(company):
	variations = [company]
	
	suffixes     = [' inc', ' inc.', ' corp', ' corp.', ' group', ' limited', ' l.p.', ' plc', ' co', ' co.', ' lp', ' ltd', ' ltd.', ' llc', ' company', ' s.a.', ' n.v.', ' ag', ' trust', 'oration', 'rporation', '.']
	replacements = [{'old': ' com', 'new': '.com'}]

	for suffix in suffixes:
		variations.append(company + suffix)
	for replacement in replacements:
		variations.append(company.replace(replacement['old'], replacement['new']))
	return variations





def estimate_runtime(start, n, total):
	now     = datetime.datetime.now()
	elapsed = now - start
	
	runtime = (elapsed / n) * (total - n)
	seconds = runtime.seconds
	hours   = seconds // 3600
	minutes = (seconds - (hours * 3600)) // 60

	if hours > 0: 
		hours_msg = str(hours) + ' hours and '
	else:
		hours_msg = ''
	
	print('Will be done in about ' + hours_msg + str(minutes) + ' minutes at ' + (now + runtime).strftime('%I:%M%p'))





print('\033[2J\033[1;1H')
print('### PARSEC TICKERS ###')

companies = db.get_companies(dbc, cursor)
tickers   = get_all_tickers(['nyse', 'nasdaq'])

if companies['success'] and tickers:
	print('Found ' + str(len(companies['data'])) + ' companies in db')
	print('Found ' + str(len(tickers)) + ' possible tickers')
	start = datetime.datetime.now()

	for i, company in enumerate(companies['data']):
		company['diff'] = replace_common_strings(company['name'])
		variations      = common_name_variations(company['diff'])
		
		for possibility in tickers.keys():
		 	diff = replace_common_strings(possibility)
		 	if diff in variations:
		 		ticker = tickers[possibility]
	 			db.saveTicker(dbc, cursor, company['cik'], ticker)
	 			break
	 	if i in [100, 1000]:
	 		estimate_runtime(start, i, len(companies['data']))
