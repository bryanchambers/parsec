import db


# Choose report
# Get company cik
# Get report data
# Reformat report data
# Calculate scores
# Store scores

dbc    = db.dbConnect('localhost', 'root', 'atlas', 'parsec')
cursor = db.getCursor(dbc)

unscored = db.getUnscoredReports(dbc, cursor)

for report in unscored['data']:
	db.getReports(dbc, cursor, report['cik'], report['release_date'])


data = db.getReports(dbc, cursor, cik, release_date, 20)









def formatRegressionData(data):
	output = {}
	output['profit_margin']    = {}
	output['return_on_equity'] = {}
	output['debt_coverage']    = {}
	output['current_leverage'] = {}
	output['total_leverage']   = {}
	output['revenue']          = {}
	output['net_income']       = {}
	output['long_term_assets'] = {}
	output['equity']           = {}

	for each row in data:
		time = int(row['release_date'].timestamp / 86400)
		
		output['profit_margin'][time]    = row['net_income'] / row['revenue']
		output['return_on_equity'][time] = row['net_income'] / (row['total_assets'] - row['total_liabilities'])
		output['debt_coverage'][time]    = row['net_income'] / row['current_liabilities']
		output['current_leverage'][time] = row['current_assets'] / row['current_liabilities']
		output['total_leverage'][time]   = row['total_assets'] / row['total_liabilities']
		output['revenue'][time]          = row['revenue']
		output['net_income'][time]       = row['net_income']
		output['long_term_assets'][time] = row['total_assets'] - row['current_assets']
		output['equity'][time]           = row['total_assets'] - row['total_liabilities']
	return output








def formatAvgData(data):
	output = {}
	output['profit_margin']    = []
	output['return_on_equity'] = []
	output['debt_coverage']    = []
	output['current_leverage'] = []
	output['total_leverage']   = []

	for each row in data:
		output['profit_margin'].append(row['net_income'] / row['revenue'])
		output['return_on_equity'].append(row['net_income'] / (row['total_assets'] - row['total_liabilities']))
		output['debt_coverage'].append(row['net_income'] / row['current_liabilities'])
		output['current_leverage'].append(row['current_assets'] / row['current_liabilities'])
		output['total_leverage'].append(row['total_assets'] / row['total_liabilities'])
	return output






def calcScores(avgData, regressionData):
	scores = {}
	scores['profit_margin']          = avgScore(avgData['profit_margin'])
	scores['return_on_equity']       = avgScore(avgData['return_on_equity'])
	scores['debt_coverage']          = avgScore(avgData['debt_coverage'])
	scores['current_leverage']       = avgScore(avgData['current_leverage'])
	scores['total_leverage']         = avgScore(avgData['total_leverage'])
	scores['profit_margin_growth']   = regressionScore(regressionData['profit_margin_growth'])
	scores['return_on_equity']       = regressionScore(regressionData['return_on_equity'])
	scores['debt_coverage']          = regressionScore(regressionData['debt_coverage'])
	scores['current_leverage']       = regressionScore(regressionData['current_leverage'])
	scores['total_leverage_growth']  = regressionScore(regressionData['total_leverage_growth'])
	scores['revenue_growth']         = regressionScore(regressionData['revenue_growth'])
	scores['net_income_growth']      = regressionScore(regressionData['net_income_growth'])
	scores['long_term_asset_growth'] = regressionScore(regressionData['long_term_asset_growth'])
	scores['equity_growth']          = regressionScore(regressionData['equity_growth'])
	return scores








def avg(data):
	n   = len(data)
	avg = { x: 0, y: 0 }
	
	for x in data:
		avg.x += x
		avg.y += data[x]
	
	avg.x /= n
	avg.y /= n
	return avg




def sigma(data):
	avg   = avg(data)
	n     = len(data)
	sigma = { x: 0, y: 0 }
	
	for x in data:
		y = data[x]
		sigma.x += (x - avg.x) ** 2
		sigma.y += (y - avg.y) ** 2

	sigma.x = (sigma.x / (n - 1)) ** 0.5
	sigma.y = (sigma.y / (n - 1)) ** 0.5
	return sigma





def correlation(data):
	avg = avg(data)
	sumXY = 0
	sumX2 = 0
	sumY2 = 0

	for x in data:
		y = data[x]
		xMinusAvg  = x - avg.x
		yMinusAvg  = y - avg.y
		xyMinusAvg = xMinusAvg * yMinusAvg
		
		xMinusAvg2 = xMinusAvg ** 2
		yMinusAvg2 = yMinusAvg ** 2

		sumXY += xyMinusAvg
		sumX2 += xMinusAvg2
		sumY2 += yMinusAvg2

	return sumXY / ((sumX2 * sumY2) ** 0.5)



def slope(data):
	sigma = sigma(data)
	return correlation(data) * (sigma.y / sigma.x)




def regressionScore(data):
	avg = avg(data)
	return slope(data) / avg.y




def avgScore(data):
	return sum(data) / len(data)