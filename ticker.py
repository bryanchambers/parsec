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
			ticker  = data[0].replace('"', '').strip()
			company = data[1].replace('"', '').strip().lower()
			if '^' not in ticker:
				if company not in tickers:
					tickers[company] = ticker
				else:
					try:
						tickers[company].append(ticker)
					except AttributeError:
						tickers[company] = [ticker]
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






def get_companies():
	companies = db.get_companies(dbc, cursor)
	if companies['success']:
		return companies['data']
	else:
		return False




def replace_common_strings(name):
	name = name.replace('the', '')
	name = name.replace('-', ' ')
	name = name.replace('&#39;', '')
	name = name.replace('co.', 'co')
	name = name.replace('inc.', 'inc')
	name = name.replace('u.s.a.', 'usa')
	name = name.replace('u.s. ', 'us ')
	name = name.replace('?', '')
	name = name.replace('!', '')
	name = name.replace(' & ', ' and ')
	name = name.replace("'", '')
	name = name.replace('hldgs', 'holdings')
	return name



def common_name_variations(company):
	return [
		company,
		company + ' inc',
		company + ' inc.',
		company + ' corp',
		company + ' corp.',
		company + ' group',
		company + ' limited',
		company + ' l.p.',
		company + ' plc',
		company + ' co',
		company + ' co.',
		company + ' lp',
		company + ' ltd',
		company + ' ltd.',
		company + ' llc',
		company + ' company',
		company + ' s.a.',
		company + ' n.v.',
		company + ' ag',
		company + ' trust',
		company + 'oration',
		company + 'rporation',
		company + 'mpany',
		company + '.',
		company.replace(' com', '.com')
	]




print(datetime.datetime.now())

companies = get_companies()
tickers   = get_all_tickers(['nyse', 'nasdaq'])
matched   = []

for company in companies:
	 company['diff'] = replace_common_strings(company['name'])
	 variations = common_name_variations(company['diff'])
	 for possibility in tickers.keys():
	 	diff = replace_common_strings(possibility)
	 	if diff in variations:
 			matched.append({
 				'name':   company['name'],
 				'ticker': tickers[possibility]
 			})
 			db.saveTicker(dbc, cursor, company['cik'], str(tickers[possibility]))
 			break

print('Matched ' + str(len(matched)) + ' of ' + str(len(companies)) + ' companies')
print(datetime.datetime.now())