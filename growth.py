import db
import datetime
import time
import sys

dbc    = db.dbConnect('localhost', 'root', 'atlas', 'parsec')
cursor = db.getCursor(dbc)


print('\033[2J\033[1;1H')
print('### PARSEC GROWTH ###')

def showCounts():
	count = db.countGrowthReports(dbc, cursor)
	total = db.countSuccessfulReports(dbc,cursor)
	if count['success'] and total['success']:
		count = count['count']
		total = total['count']
		percentage = int((float(count) / total) * 100)
		print('\n\nProcessed ' + str(count) + '/' + str(total) + ' reports')
		print(str(percentage) + '%\n')




def updateStatus(msg):
	timestamp = datetime.datetime.now().strftime("%d %b %I:%M:%S%p")
	output    = msg + '   ' + timestamp + '   '
	sys.stdout.write('\r')
	sys.stdout.write(output)
	sys.stdout.flush()







def formatRegressionData(data):
	output = {}
	output['profit_margin_growth']    = {}
	output['return_on_equity_growth'] = {}
	output['debt_coverage_growth']    = {}
	output['current_leverage_growth'] = {}
	output['total_leverage_growth']   = {}
	output['revenue_growth']          = {}
	output['net_income_growth']       = {}
	output['long_term_asset_growth'] = {}
	output['equity_growth']           = {}

	for row in data['data']:
		release_date = datetime.datetime.combine(row['release_date'], datetime.datetime.min.time())
		epoch = datetime.datetime.utcfromtimestamp(0)
		seconds = (release_date - epoch).total_seconds()
		timestamp = int(float(seconds) / 86400)
		
		output['profit_margin_growth'][timestamp]    = clipGrowthData(row['profit_margin'])
		output['return_on_equity_growth'][timestamp] = clipGrowthData(row['return_on_equity'])
		output['debt_coverage_growth'][timestamp]    = clipGrowthData(row['debt_coverage'])
		output['current_leverage_growth'][timestamp] = clipGrowthData(row['current_leverage'])
		output['total_leverage_growth'][timestamp]   = clipGrowthData(row['total_leverage'])
		output['revenue_growth'][timestamp]          = clipGrowthData(row['revenue'])
		output['net_income_growth'][timestamp]       = clipGrowthData(row['net_income'])
		output['long_term_asset_growth'][timestamp]  = clipGrowthData(row['total_assets'] - row['current_assets'])
		output['equity_growth'][timestamp]           = clipGrowthData(row['total_assets'] - row['total_liabilities'])
	return output






def clipGrowthData(value):
	if value < 1:
		return 1
	else:
		return value







def calcGrowth(data):
	growth = {}
	growth['profit_margin_growth']    = getGrowth(data['profit_margin_growth'])
	growth['return_on_equity_growth'] = getGrowth(data['return_on_equity_growth'])
	growth['debt_coverage_growth']    = getGrowth(data['debt_coverage_growth'])
	growth['current_leverage_growth'] = getGrowth(data['current_leverage_growth'])
	growth['total_leverage_growth']   = getGrowth(data['total_leverage_growth'])
	growth['revenue_growth']          = getGrowth(data['revenue_growth'])
	growth['net_income_growth']       = getGrowth(data['net_income_growth'])
	growth['long_term_asset_growth']  = getGrowth(data['long_term_asset_growth'])
	growth['equity_growth']           = getGrowth(data['equity_growth'])
	return growth











def calcGrowthWrapper(report):
	min_reports    = 10
	max_date_range = 48
	reports = db.getGrowthReportsForCalc(dbc, cursor, report['cik'], report['release_date'])
	if reports['success']:
		count = len(reports['data'])
		if count >= min_reports:
			date_range_start = reports['data'][0]['release_date']
			date_range_end   = reports['data'][count - 1]['release_date']
			date_range = (date_range_start - date_range_end).days / 30
			if date_range <= max_date_range:
				formatted = formatRegressionData(reports)
				growth    = calcGrowth(formatted)
				pm  = growth['profit_margin_growth'] 
				roe = growth['return_on_equity_growth']
				dc  = growth['debt_coverage_growth']
				cl  = growth['current_leverage_growth']
				tl  = growth['total_leverage_growth']
				rv  = growth['revenue_growth']
				ni  = growth['net_income_growth']
				lta = growth['long_term_asset_growth']
				eq  = growth['equity_growth']
				return {'success': True, 'data': (pm, roe, dc, cl, tl, rv, ni, lta, eq)}
			else: return {'success': True, 'data': (0, 0, 0, 0, 0, 0, 0, 0, 0), 'errors': 'Date range of ' + str(date_range) + 'm exceeds ' + str(max_date_range) + ' month max'}
		else: return {'success': True, 'data': (0, 0, 0, 0, 0, 0, 0, 0, 0), 'errors': 'Only found ' + str(count) + ' of ' + str(min_reports) + ' required reports'}
	else: return {'success': False, 'errors': reports['errors']}













def getAvg(data):
	n   = len(data)
	avg = {}
	avg['x'] = 0
	avg['y'] = 0
	
	for x in data:
		avg['x'] += x
		avg['y'] += data[x]
	
	avg['x'] /= n
	avg['y'] /= n
	return avg




def getSigma(data):
	avg   = getAvg(data)
	n     = len(data)
	sigma = {}
	sigma['x'] = 0
	sigma['y'] = 0
	
	for x in data:
		y = data[x]
		sigma['x'] += (x - avg['x']) ** 2
		sigma['y'] += (y - avg['y']) ** 2

	sigma['x'] = (sigma['x'] / (n - 1)) ** 0.5
	sigma['y'] = (sigma['y'] / (n - 1)) ** 0.5
	return sigma





def correlation(data):
	avg = getAvg(data)
	sumXY = 0
	sumX2 = 0
	sumY2 = 0

	for x in data:
		y = data[x]
		xMinusAvg  = x - avg['x']
		yMinusAvg  = y - avg['y']
		xyMinusAvg = xMinusAvg * yMinusAvg
		
		xMinusAvg2 = xMinusAvg ** 2
		yMinusAvg2 = yMinusAvg ** 2

		sumXY += xyMinusAvg
		sumX2 += xMinusAvg2
		sumY2 += yMinusAvg2

	if sumX2 == 0 or sumY2 == 0:
		return 1
	else:
		correlation = sumXY / ((sumX2 * sumY2) ** 0.5)
		return correlation



def slope(data):
	sigma = getSigma(data)
	return correlation(data) * (sigma['y'] / sigma['x'])




def getGrowth(data):
	growth = (slope(data) / getAvg(data)['y']) * 8000000
	if growth > 32000:
		return 32000
	elif growth < -32000:
		return -32000
	else:
		return int(growth)




def avgScore(data):
	return sum(data) / len(data)















showCounts()

complete = False
error    = False
batches  = 0

while not complete and not error:
	updateStatus('Loading reports')
	reports = db.getGrowthReports(dbc, cursor)
	if(reports['success']):
		if(len(reports['data']) > 0):
			batches += 1
			updateStatus('Processing batch ' + str(batches))
			for report in reports['data']:
				growth = calcGrowthWrapper(report)
				if growth['success']:
					result = db.saveGrowth(dbc, cursor, growth['data'], report['id'])
					if not result['success']:
						updateStatus('Error while saving growth to report' + str(report['id']))
						print('\n' + result['errors'] + '\n')
						error = True
				else:
					updateStatus('Error while loading reports')
					print('\n' + growth['errors'] + '\n')
					error = True
			updateStatus('Finished batch ' + str(batches))
			if batches % 100 == 0: showCounts()
		else:
			updateStatus('No reports to process')
			complete = True
	else:
		updateStatus('Error while loading reports')
		print('\n' + reports['errors'] + '\n')
		error = True


showCounts()