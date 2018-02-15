import db
import datetime
import sys

dbc    = db.dbConnect('localhost', 'root', 'atlas', 'parsec')
cursor = db.getCursor(dbc)


print('\033[2J\033[1;1H')
print('### PARSEC RATIOS ###')

def showCounts():
	count = db.countRatioReports(dbc, cursor)
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
	



showCounts()

complete = False
error    = False
batches  = 0

while not complete and not error:
	updateStatus('Loading reports')
	reports = db.getRatioReports(dbc, cursor)
	if(reports['success']):
		if(len(reports['data']) > 0):
			batches += 1
			updateStatus('Processing batch ' + str(batches))
			for report in reports['data']:
				result = db.saveRatios(dbc, cursor, calcRatios(report), report['id'])
				if(not result['success']):
					updateStatus('Error while saving ratios to report ' + str(report['id']))
					print('\n' + result['errors'] + '\n')
					error = True
			updateStatus('Finished batch ' + str(batches))
			if batches % 100 == 0: showCounts()
		else:
			updateStatus('No reports to process')
			complete = True
	else:
		updateStatus('Error while loading reports')
		print('\n' + result['errors'] + '\n')
		error = True



showCounts()