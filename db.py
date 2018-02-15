import MySQLdb
import datetime

def dbConnect(host, user, password, db):
	return MySQLdb.connect(host, user, password, db)

def getCursor(connection):
	return connection.cursor()





def createTable(cursor, table):
	query = {}

	query['reports'] = """CREATE TABLE IF NOT EXISTS reports(
		id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
		cik INT NOT NULL,
		release_date DATE NOT NULL,
		filename VARCHAR(255) NOT NULL,
		success TINYINT,
		net_income BIGINT,
		operating_income BIGINT,
		gross_income BIGINT,
		revenue BIGINT,
		total_assets BIGINT,
		total_liabilities BIGINT,
		current_assets BIGINT,
		current_liabilities BIGINT,
		operating_cash_flow BIGINT,
		investing_cash_flow BIGINT,
		financing_cash_flow BIGINT,
		starting_cash BIGINT,
		ending_cash BIGINT,
		profit_margin SMALLINT,
		return_on_equity SMALLINT,
		debt_coverage SMALLINT,
		current_leverage SMALLINT,
		total_leverage SMALLINT,
		profit_margin_growth SMALLINT,
		return_on_equity_growth SMALLINT,
		debt_coverage_growth SMALLINT,
		current_leverage_growth SMALLINT,
		total_leverage_growth SMALLINT,
		revenue_growth SMALLINT,
		net_income_growth SMALLINT,
		long_term_asset_growth SMALLINT,
		equity_growth SMALLINT)"""

	query['companies'] = """CREATE TABLE IF NOT EXISTS companies(
		cik INT NOT NULL PRIMARY KEY,
		name VARCHAR(255))"""

	try: 
		cursor.execute(query[table])
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)

	return {'success': success, 'errors': errors}





def prepData(report, data):
	d = {}
	for row in data['output']:
		try:
			d[row['header']] = row['values'][0]
			d[row['header'] + '_ext'] = row['values'][1]
		except TypeError:
			d[row['header']] = row['values']

	return (report['cik'], report['date'], report['filename'],
			d['net_income'], d['operating_income'], d['gross_income'], d['revenue'],
			d['total_assets'], d['total_liabilities'], d['current_assets'], d['current_liabilities'],
			d['operating_cash_flow'], d['investing_cash_flow'], d['financing_cash_flow'], d['starting_cash'], d['ending_cash'])





def addReportSuccessOld(dbc, cursor, data):
	query = """INSERT INTO reports(
		cik, release_date, filename, success,
		net_income, operating_income, gross_income, revenue,
		total_assets, total_liabilities, current_assets, current_liabilities,
		operating_cash_flow, investing_cash_flow, financing_cash_flow, starting_cash, ending_cash) 
		VALUES(%s, %s, %s, 1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

	try: 
		cursor.execute(query, data)
		dbc.commit()
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)

	return {'success': success, 'errors': errors}





def addReportSuccess(dbc, cursor, data, id):
	query = """UPDATE reports SET 
		cik = %s, release_date = %s, filename = %s, success = 1,
		net_income = %s, operating_income = %s, gross_income = %s, revenue = %s,
		total_assets = %s, total_liabilities = %s, current_assets = %s, current_liabilities = %s,
		operating_cash_flow = %s, investing_cash_flow = %s, financing_cash_flow = %s, starting_cash = %s, ending_cash = %s 
		WHERE id = """ + str(id) + " LIMIT 1"

	try: 
		cursor.execute(query, data)
		dbc.commit()
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)
		print(errors)

	return {'success': success, 'errors': errors}






def saveRatios(dbc, cursor, data, id):
	query = """UPDATE reports SET 
		profit_margin = %s, return_on_equity = %s, debt_coverage = %s, current_leverage = %s, total_leverage = %s
		WHERE id = """ + str(id) + " LIMIT 1"

	try: 
		cursor.execute(query, data)
		dbc.commit()
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)

	return {'success': success, 'errors': errors}



def saveAverages(dbc, cursor, data, id):
	query = """UPDATE reports SET 
		profit_margin_avg = %s, return_on_equity_avg = %s, debt_coverage_avg = %s, current_leverage_avg = %s, total_leverage_avg = %s
		WHERE id = """ + str(id) + " LIMIT 1"

	try: 
		cursor.execute(query, data)
		dbc.commit()
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)
		print(errors)

	return {'success': success, 'errors': errors}



def saveGrowth(dbc, cursor, data, id):
	query = """UPDATE reports SET 
		profit_margin_growth = %s, return_on_equity_growth = %s, debt_coverage_growth = %s, current_leverage_growth = %s, total_leverage_growth = %s, revenue_growth = %s, net_income_growth = %s, long_term_asset_growth = %s, equity_growth = %s
		WHERE id = """ + str(id) + " LIMIT 1"

	try: 
		cursor.execute(query, data)
		dbc.commit()
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)
		print(errors)

	return {'success': success, 'errors': errors}






def saveScores(dbc, cursor, data, id):
	query = """UPDATE reports SET 
		profit_margin_score = %s, return_on_equity_score = %s, debt_coverage_score = %s, current_leverage_score = %s, total_leverage_score = %s, profit_margin_growth_score = %s, return_on_equity_growth_score = %s, debt_coverage_growth_score = %s, current_leverage_growth_score = %s, total_leverage_growth_score = %s, revenue_growth_score = %s, net_income_growth_score = %s, long_term_asset_growth_score = %s, equity_growth_score = %s
		WHERE id = """ + str(id) + " LIMIT 1"

	try: 
		cursor.execute(query, data)
		dbc.commit()
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)
		print(errors)

	return {'success': success, 'errors': errors}






def saveOverallScore(dbc, cursor, data, id):
	query = "UPDATE reports SET overall_score = %s WHERE id = " + str(id) + " LIMIT 1"

	try: 
		cursor.execute(query, data)
		dbc.commit()
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)
		print(errors)

	return {'success': success, 'errors': errors}







def addReportFail(dbc, cursor, report):
	query = "INSERT INTO reports(cik, release_date, filename, success) VALUES(%s, %s, %s, 0)"

	try: 
		cursor.execute(query, [report['cik'], report['date'], report['filename']])
		dbc.commit()
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)

	return {'success': success, 'errors': errors}



def addReport(dbc, cursor, report):
	query = "INSERT INTO reports(cik, release_date, filename) VALUES(%s, %s, %s)"

	try: 
		cursor.execute(query, [report['cik'], report['date'], report['filename']])
		dbc.commit()
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)

	return {'success': success, 'errors': errors}





def getReportID(dbc, cursor):
	try: 
		cursor.execute("SELECT LAST_INSERT_ID() from reports")
		dbc.commit()
		result  = cursor.fetchall()
		id      = result[0][0]
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)

	return {'success': success, 'id': id, 'errors': errors}






def countReports(dbc, cursor):
	try: 
		cursor.execute("SELECT COUNT(*) FROM reports")
		dbc.commit()
		result  = cursor.fetchall()
		count  = result[0][0]
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		errors  = str(e)
		success = False

	return {'success': success, 'count': count, 'errors': errors}



def countSuccessfulReports(dbc, cursor):
	try: 
		cursor.execute("SELECT COUNT(*) FROM reports WHERE success = 1")
		dbc.commit()
		result  = cursor.fetchall()
		count  = result[0][0]
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		errors  = str(e)
		success = False

	return {'success': success, 'count': count, 'errors': errors}




def countRatioReports(dbc, cursor):
	try: 
		cursor.execute("SELECT COUNT(*) FROM reports WHERE success = 1 AND profit_margin IS NOT NULL")
		dbc.commit()
		result  = cursor.fetchall()
		count  = result[0][0]
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		errors  = str(e)
		success = False

	return {'success': success, 'count': count, 'errors': errors}




def countAvgReports(dbc, cursor):
	try: 
		cursor.execute("SELECT COUNT(*) FROM reports WHERE success = 1 AND profit_margin IS NOT NULL AND profit_margin_avg IS NOT NULL")
		dbc.commit()
		result  = cursor.fetchall()
		count  = result[0][0]
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		errors  = str(e)
		success = False

	return {'success': success, 'count': count, 'errors': errors}





def countGrowthReports(dbc, cursor):
	try: 
		cursor.execute("SELECT COUNT(*) FROM reports WHERE success = 1 AND profit_margin IS NOT NULL AND profit_margin_growth IS NOT NULL")
		dbc.commit()
		result  = cursor.fetchall()
		count  = result[0][0]
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		errors  = str(e)
		success = False

	return {'success': success, 'count': count, 'errors': errors}






def countScoredReports(dbc, cursor):
	try: 
		cursor.execute("SELECT COUNT(*) FROM reports WHERE success = 1 AND profit_margin IS NOT NULL AND profit_margin_score IS NOT NULL")
		dbc.commit()
		result  = cursor.fetchall()
		count  = result[0][0]
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		count   = False
		errors  = str(e)
		success = False

	return {'success': success, 'count': count, 'errors': errors}





def companyExists(dbc, cursor, cik):
	try: 
		cursor.execute("SELECT COUNT(*) FROM companies WHERE cik = %s", [cik])
		dbc.commit()
		result  = cursor.fetchall()
		exists  = result[0][0]
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		errors  = str(e)
		success = False

	return {'success': success, 'exists': exists, 'errors': errors}





def addCompany(dbc, cursor, report):
	query = "INSERT INTO companies(cik, name) VALUES(%s, %s)"

	try: 
		cursor.execute(query, [report['cik'], report['company']])
		dbc.commit()
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)

	return {'success': success, 'errors': errors}




def getLastReportYear(dbc, cursor):
	try: 
		cursor.execute("SELECT MAX(release_date) from reports")
		dbc.commit()
		result  = cursor.fetchall()
		date    = result[0][0]
		if(date): year = date.year
		else:     year = datetime.datetime.now().year
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)

	return {'success': success, 'year': year, 'errors': errors}












def dbRead(dbc, cursor, query, parameters):
	try: 
		cursor.execute(query, parameters)
		dbc.commit()
		
		fields = []
		for field in cursor.description: fields.append(field[0])

		result = cursor.fetchall()
		data   = []
		for line in result:
			row = {}
			for i in range(0, len(line)):
				field = fields[i]
				value = line[i]
				row[field] = value
			data.append(row)
		return {'success': True, 'data': data }

	except MySQLdb.Error, errors:
		return {'success': False, 'errors': str(errors)}



def getReports(dbc, cursor, cik, release_date, n):
	query = "SELECT * FROM reports WHERE cik = " + str(cik) + " AND release_date <= '" + release_date.strftime('%Y-%m-%d') + "' AND success = 1 ORDER BY release_date DESC LIMIT " + str(n)
	return dbRead(dbc, cursor, query, None)



def getQuarterDateRange(year, qtr):
	monthEnd   = int(qtr * 3)
	monthStart = monthEnd - 4
	if(monthStart <  1): monthStart =  1
	if(monthEnd   > 12): monthEnd   = 12

	qtrStart = str(year) + '-' + format(monthStart, '02') + '-01'
	qtrEnd   = str(year) + '-' + format(monthEnd,   '02') + '-01'
	return { 'start': qtrStart, 'end': qtrEnd }




def getCompletedReportList(dbc, cursor, year, qtr):
	qtrDates   = getQuarterDateRange(year, qtr)
	query      = "SELECT filename FROM reports WHERE release_date >= '" + qtrDates['start'] + "' AND release_date <= '" + qtrDates['end'] + "'"
	reports    = dbRead(dbc, cursor, query, None)

	if(reports['success']):
		output = {}
		for row in reports['data']: output[row['filename']] = True
		reports['data'] = output
	return reports




def reportExists(dbc, cursor, filename):
	query   = "SELECT * FROM reports WHERE filename = '" + filename + "'"
	reports = dbRead(dbc, cursor, query, None)

	if(reports['success'] and len(reports['data']) > 0):
		reports['data'] = True
	else:
		reports['data'] = False
	return reports



def getGrowthReports(dbc, cursor):
	query = "SELECT * FROM reports WHERE success = 1 AND profit_margin IS NOT NULL AND profit_margin_growth IS NULL ORDER BY release_date DESC LIMIT 10"
	return dbRead(dbc, cursor, query, None)


def getGrowthReportsForCalc(dbc, cursor, cik, release_date):
	query = "SELECT * FROM reports WHERE cik = " + str(cik) + " AND success = 1 AND profit_margin IS NOT NULL AND release_date <= '" + release_date.strftime('%Y-%m-%d') + "' ORDER BY release_date DESC LIMIT 12"
	return dbRead(dbc, cursor, query, None)



def getAvgReports(dbc, cursor):
	query = "SELECT * FROM reports WHERE success = 1 AND profit_margin IS NOT NULL AND profit_margin_avg IS NULL ORDER BY release_date DESC LIMIT 10"
	return dbRead(dbc, cursor, query, None)


def getAvgReportsForCalc(dbc, cursor, cik, release_date):
	query = "SELECT * FROM reports WHERE cik = " + str(cik) + " AND success = 1 AND profit_margin IS NOT NULL AND release_date <= '" + release_date.strftime('%Y-%m-%d') + "' ORDER BY release_date DESC LIMIT 6"
	return dbRead(dbc, cursor, query, None)


def getRatioReports(dbc, cursor):
	query = "SELECT * FROM reports WHERE success = 1 AND profit_margin IS NULL LIMIT 100"
	return dbRead(dbc, cursor, query, None)

def getUnscoredReports(dbc, cursor):
	query = "SELECT * FROM reports WHERE success = 1 AND profit_margin_growth IS NOT NULL AND profit_margin_score IS NULL LIMIT 100"
	return dbRead(dbc, cursor, query, None)


def getOverallReports(dbc, cursor):
	query = "SELECT * FROM reports WHERE success = 1 AND profit_margin_score IS NOT NULL AND overall_score IS NULL LIMIT 100"
	return dbRead(dbc, cursor, query, None)