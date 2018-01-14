import db

dbc    = db.dbConnect('localhost', 'root', 'atlas', 'parsec')
cursor = db.getCursor(dbc)

response = db.getUncalculatedReports(dbc, cursor)


reports = response['data']







def calcRatio(numerator, denominator):
	if(denominator == 0):
		if  (numerator == 0): return    0
		elif(numerator  > 0): return  320
		else:                 return -320 
	else:
		return float(numerator) / denominator 





def clipAndScale(value):
	if(value >  320): value =  320
	if(value < -320): value = -320
	return int(value * 100)




def calcRatios(report):
	net_income          = report['net_income']
	revenue             = report['revenue']
	current_assets      = report['current_assets']
	current_liabilities = report['current_liabilities']
	total_assets        = report['total_assets']
	total_liabilities   = report['total_liabilities']
	profit_margin       = clipAndScale(calcRatio(net_income, revenue))
	return_on_equity    = clipAndScale(calcRatio(net_income, total_assets - total_liabilities))
	debt_coverage       = clipAndScale(calcRatio(net_income, current_liabilities))
	current_leverage    = clipAndScale(calcRatio(current_assets, current_liabilities))
	total_leverage      = clipAndScale(calcRatio(total_assets, total_liabilities))
	return (profit_margin, return_on_equity, debt_coverage, current_leverage, total_leverage)
	

for report in reports:
	#print(calcRatios(report))
	db.addRatios(dbc, cursor, calcRatios(report), report['id'])