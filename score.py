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




def score(data):
	avg = avg(data)
	return slope(data) / avg.y