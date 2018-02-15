import db
import datetime
import sys

dbc    = db.dbConnect('localhost', 'root', 'atlas', 'parsec')
cursor = db.getCursor(dbc)


print('\033[2J\033[1;1H')
print('### PARSEC AVERAGES ###')

def showCounts():
	count = db.countAvgReports(dbc, cursor)
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




def calcAverages(report):
	min_reports    = 4
	max_date_range = 24
	reports = db.getAvgReportsForCalc(dbc, cursor, report['cik'], report['release_date'])
	if reports['success']:
		count = len(reports['data'])
		if count >= min_reports:
			date_range_start = reports['data'][0]['release_date']
			date_range_end   = reports['data'][count - 1]['release_date']
			date_range = (date_range_start - date_range_end).days / 30
			if date_range <= max_date_range:
				profit_margin_avg    = 0
				return_on_equity_avg = 0
				debt_coverage_avg    = 0
				current_leverage_avg = 0
				total_leverage_avg   = 0
				for report in reports['data']:
					profit_margin_avg    += report['profit_margin']
					return_on_equity_avg += report['return_on_equity']
					debt_coverage_avg    += report['debt_coverage']
					current_leverage_avg += report['current_leverage']
					total_leverage_avg   += report['total_leverage']
				profit_margin_avg    = int(profit_margin_avg    / count)
				return_on_equity_avg = int(return_on_equity_avg / count)
				debt_coverage_avg    = int(debt_coverage_avg    / count)
				current_leverage_avg = int(current_leverage_avg / count)
				total_leverage_avg   = int(total_leverage_avg   / count)
				return {'success': True, 'data': (profit_margin_avg, return_on_equity_avg, debt_coverage_avg, current_leverage_avg, total_leverage_avg)}
			else: return {'success': True, 'data': (0, 0, 0, 0, 0), 'errors': 'Date range of ' + str(date_range) + 'm exceeds ' + str(max_date_range) + ' month max'}
		else: return {'success': True, 'data': (0, 0, 0, 0, 0), 'errors': 'Only found ' + str(count) + ' of ' + str(min_reports) + ' required reports'}
	else: return {'success': False, 'errors': reports['errors']}



showCounts()

complete = False
error    = False
batches  = 0

while not complete and not error:
	updateStatus('Loading reports')
	reports = db.getAvgReports(dbc, cursor)
	if(reports['success']):
		if(len(reports['data']) > 0):
			batches += 1
			updateStatus('Processing batch ' + str(batches))
			for report in reports['data']:
				averages = calcAverages(report)
				if averages['success']:
					result = db.saveAverages(dbc, cursor, averages['data'], report['id'])
					if not result['success']:
						updateStatus('Error while saving averages to report' + str(report['id']))
						print('\n' + result['errors'] + '\n')
						error = True
				else:
					updateStatus('Error while loading reports')
					print('\n' + averages['errors'] + '\n')
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