



import db
import datetime
import sys

dbc    = db.dbConnect('localhost', 'root', 'atlas', 'parsec')
cursor = db.getCursor(dbc)


print('\033[2J\033[1;1H')
print('### PARSEC OVERALL ###')






# profit_margin
# return_on_equity
# debt_coverage
# current_leverage
# total_leverage


# profit_margin_growth
# return_on_equity_growth

# debt_coverage_growth
# current_leverage_growth
# total_leverage_growth

# revenue_growth
# net_income_growth
# long_term_asset_growth
# equity_growth





components = [{
		"name": "snapshot",
		"weight": 0.6,
		"components": [{
				"name": "efficiency",
				"weight": 0.5,
				"components": [
					{ "name": "profit_margin",           "weight": 0.5 },
					{ "name": "return_on_equity",        "weight": 0.5 }
				]
			}, {
				"name": "debt",
				"weight": 0.5,
				"components": [
					{ "name": "debt_coverage",           "weight": 0.25 },
					{ "name": "current_leverage",        "weight": 0.25 },
					{ "name": "total_leverage",          "weight": 0.50 }
				]
			}
		]
	}, {
		"name": "trend",
		"weight": 0.4,
		"components": [{
				"name": "efficiency",
				"weight": 0.15,
				"components": [
					{ "name": "profit_margin_growth",    "weight": 0.5 },
					{ "name": "return_on_equity_growth", "weight": 0.5 }
				]
			}, {
				"name": "debt",
				"weight": 0.25,
				"components": [
					{ "name": "debt_coverage_growth",    "weight": 0.15 },
					{ "name": "current_leverage_growth", "weight": 0.15 },
					{ "name": "total_leverage_growth",   "weight": 0.70 }
				]
			}, {
				"name": "growth",
				"weight": 0.60,
				"components": [
					{ "name": "revenue_growth",          "weight": 0.40 },
					{ "name": "net_income_growth",       "weight": 0.25 },
					{ "name": "long_term_asset_growth",  "weight": 0.25 },
					{ "name": "equity_growth",           "weight": 0.10 }
				]
			}
		]
	}
]




weights = {}


def dig(components, parent_weight):
	for component in components:
		weight = parent_weight * component['weight']
		if 'components' in component:
			dig(component['components'], weight)
		else:
			name = component['name'] + '_score'
			weights[name] = weight




dig(components, 1)

total = 0
for weight in weights:
	total += weights[weight]












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




def calcOverallScore(report):
	overall = 0
	for score in report:
		if score in weights:
			overall += report[score] * weights[score]
	overall = int(round(overall, 0))
	return (overall,)
	



showCounts()

complete = False
error    = False
batches  = 0

while not complete and not error:
	updateStatus('Loading reports')
	reports = db.getOverallReports(dbc, cursor)
	if(reports['success']):
		if(len(reports['data']) > 0):
			batches += 1
			updateStatus('Processing batch ' + str(batches))
			for report in reports['data']:
				result = db.saveOverallScore(dbc, cursor, calcOverallScore(report), report['id'])
				if(not result['success']):
					updateStatus('Error while saving overall score to report ' + str(report['id']))
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