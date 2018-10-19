import requests
import db
import datetime

dbc    = db.dbConnect('localhost', 'root', 'atlas', 'parsec')
cursor = db.getCursor(dbc)





def get_pe_batch(ticker_batch):
	quotes = requests.get('https://api.iextrading.com/1.0/stock/market/batch?symbols=' + ','.join(ticker_batch) + '&types=quote').json()
	
	for company in companies['data']:
		ticker = company['ticker']
		if ticker in quotes:
			if 'peRatio' in quotes[ticker]['quote']:
				pe_ratio = quotes[ticker]['quote']['peRatio']
				if pe_ratio:
					company['pe_ratio'] = int(float(pe_ratio) * 10)





def get_pe_ratios():
	print('Downloading pe ratios')
	start  = datetime.datetime.now()
	finish = start

	ticker_batch = []
	for i, company in enumerate(companies['data']):
		ticker_batch.append(company['ticker'])
		
		if len(ticker_batch) >= 100:
			get_pe_batch(ticker_batch)
			ticker_batch = []

		if datetime.datetime.now() > finish and i > 100:
	 		finish = estimate_runtime(start, i, len(companies['data']))

	if len(ticker_batch) > 0:
		get_pe_batch(ticker_batch)
	print('Done')






def get_pe_score(pe):
	pe_max = 50
	pe_min = 5

	if pe < 0:
		return 0

	scale = 100 / float(pe_max - pe_min)
	score = 100 - (((float(pe) / 10) * scale) - (pe_min * scale))

	if score > 100: score = 100
	if score <   0: score = 0
	return int(score)





def estimate_runtime(start, n, total):
	now     = datetime.datetime.now()
	elapsed = now - start
	
	runtime = (elapsed / n) * (total - n)
	seconds = runtime.seconds
	hours   = seconds // 3600
	minutes = (seconds - (hours * 3600)) // 60

	if   hours == 0: hours_msg = ''
	elif hours == 1: hours_msg = '1 hour'
	else:            hours_msg = str(hours) + ' hours'
	
	if   minutes == 0: minutes_msg = ''
	elif minutes == 1: minutes_msg = '1 minute'
	else:              minutes_msg = str(minutes) + ' minutes'
	
	if hours > 0 and minutes > 0: minutes_msg = ' and ' + minutes_msg

	if   seconds > 60: print('Will be done in about ' + hours_msg + minutes_msg + ' at ' + (now + runtime).strftime('%I:%M%p'))
	elif seconds >  0: print('Will be done in about ' + str(seconds) + ' seconds')
	return now + runtime





print('\033[2J\033[1;1H')
print('### PARSEC QUOTES ###')

companies = db.get_listed_companies(dbc, cursor)

if companies['success']:
	print('Found ' + str(len(companies['data'])) + ' companies with tickers')
	get_pe_ratios()

	start  = datetime.datetime.now()
	finish = start

	print('Saving pe ratios and scores')
	for i, company in enumerate(companies['data']):
		if 'pe_ratio' in company:
			pe_ratio = company['pe_ratio']
			pe_score = get_pe_score(pe_ratio)
			db.save_pe(dbc, cursor, company['cik'], pe_ratio, pe_score)

		if datetime.datetime.now() > finish and i > 100:
	 		finish = estimate_runtime(start, i, len(companies['data']))
	print('Done\n')
