import db
import datetime
import sys

dbc    = db.dbConnect('localhost', 'root', 'atlas', 'parsec')
cursor = db.getCursor(dbc)


print('\033[2J\033[1;1H')
print('### PARSEC SCORES ###')

def showCounts():
	count = db.countScoredReports(dbc, cursor)
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








def score(value, maximum):
	if value <= 0:
		return 0
	elif value > maximum:
		return 100
	else:
		return int(value * (100 / float(maximum)))





def calcScores(report):
	profit_margin_score           = score(report['profit_margin_avg'],          50)
	return_on_equity_score        = score(report['return_on_equity_avg'],      100)
	debt_coverage_score           = score(report['debt_coverage_avg'],         300)
	current_leverage_score        = score(report['current_leverage_avg'],     1000)
	total_leverage_score          = score(report['total_leverage_avg'],       1000)
	profit_margin_growth_score    = score(report['profit_margin_growth'],    30000)
	return_on_equity_growth_score = score(report['return_on_equity_growth'], 30000)
	debt_coverage_growth_score    = score(report['debt_coverage_growth'],    30000)
	current_leverage_growth_score = score(report['current_leverage_growth'], 30000)
	total_leverage_growth_score   = score(report['total_leverage_growth'],   30000)
	revenue_growth_score          = score(report['revenue_growth'],          30000)
	net_income_growth_score       = score(report['net_income_growth'],       30000)
	long_term_asset_growth_score  = score(report['long_term_asset_growth'],  30000)
	equity_growth_score           = score(report['equity_growth'],           30000)
	return (profit_margin_score, return_on_equity_score, debt_coverage_score, current_leverage_score, total_leverage_score, profit_margin_growth_score, return_on_equity_growth_score, debt_coverage_growth_score, current_leverage_growth_score, total_leverage_growth_score, revenue_growth_score, net_income_growth_score, long_term_asset_growth_score, equity_growth_score)
	



showCounts()

complete = False
error    = False
batches  = 0

while not complete and not error:
	updateStatus('Loading reports')
	reports = db.getUnscoredReports(dbc, cursor)
	if(reports['success']):
		if(len(reports['data']) > 0):
			batches += 1
			updateStatus('Processing batch ' + str(batches))
			for report in reports['data']:
				result = db.saveScores(dbc, cursor, calcScores(report), report['id'])
				if(not result['success']):
					updateStatus('Error while saving scores to report ' + str(report['id']))
					print('\n' + result['errors'] + '\n')
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