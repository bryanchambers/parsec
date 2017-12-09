import db
import time

# Choose report
# Get company cik
# Get report data
# Reformat report data
# Calculate scores
# Store scores

dbc    = db.dbConnect('localhost', 'root', 'atlas', 'parsec')
cursor = db.getCursor(dbc)












def formatRegressionData(data):
	output = {}
	output['profit_margin_growth']    = {}
	output['return_on_equity_growth'] = {}
	output['debt_coverage_growth']    = {}
	output['current_leverage_growth'] = {}
	output['total_leverage_growth']   = {}
	output['revenue_growth']          = {}
	output['net_income_growth']       = {}
	output['long_term_assets_growth'] = {}
	output['equity_growth']           = {}

	for row in data:
		timestamp = int(time.mktime(row['release_date'].timetuple()) / 86400)
		
		output['profit_margin_growth'][timestamp]    = row['net_income'] / row['revenue']
		output['return_on_equity_growth'][timestamp] = row['net_income'] / (row['total_assets'] - row['total_liabilities'])
		output['debt_coverage_growth'][timestamp]    = row['net_income'] / row['current_liabilities']
		output['current_leverage_growth'][timestamp] = row['current_assets'] / row['current_liabilities']
		output['total_leverage_growth'][timestamp]   = row['total_assets'] / row['total_liabilities']
		output['revenue_growth'][timestamp]          = row['revenue']
		output['net_income_growth'][timestamp]       = row['net_income']
		output['long_term_assets_growth'][timestamp] = row['total_assets'] - row['current_assets']
		output['equity_growth'][timestamp]           = row['total_assets'] - row['total_liabilities']
	return output








def formatAvgData(data):
	output = {}
	output['profit_margin']    = []
	output['return_on_equity'] = []
	output['debt_coverage']    = []
	output['current_leverage'] = []
	output['total_leverage']   = []

	for row in data:
		output['profit_margin'].append(row['net_income']        / row['revenue'])
		output['return_on_equity'].append(row['net_income']     / (row['total_assets'] - row['total_liabilities']))
		output['debt_coverage'].append(row['net_income']        / row['current_liabilities'])
		output['current_leverage'].append(row['current_assets'] / row['current_liabilities'])
		output['total_leverage'].append(row['total_assets']     / row['total_liabilities'])
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

	return sumXY / ((sumX2 * sumY2) ** 0.5)



def slope(data):
	sigma = getSigma(data)
	return correlation(data) * (sigma['y'] / sigma['x'])




def regressionScore(data):
	return slope(data) / getAvg(data)['y']




def avgScore(data):
	return sum(data) / len(data)













unscored = db.getUnscoredReports(dbc, cursor)

if(unscored['success']):
	for report in unscored['data']:
		avgReports        = db.getReports(dbc, cursor, report['cik'], report['release_date'], 6)
		regressionReports = db.getReports(dbc, cursor, report['cik'], report['release_date'], 20)
		print(len(avgReports['data']))
		if(avgReports['success'] and regressionReports['success']):
			avgData        = formatAvgData(avgReports['data'])
			regressionData = formatRegressionData(regressionReports['data'])
			#print(avgData['profit_margin'])
			#scores         = calcScores(avgData, regressionData)
			#print(scores)