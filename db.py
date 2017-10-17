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
		net_income INT,
		operating_income INT,
		gross_income INT,
		revenue INT,
		total_assets INT,
		total_liabilities INT,
		current_assets INT,
		current_liabilities INT,
		operating_cash_flow INT,
		investing_cash_flow INT,
		financing_cash_flow INT,
		starting_cash INT,
		ending_cash INT,
		profit_margin FLOAT,
		return_on_equity FLOAT,
		debt_coverage FLOAT,
		current_leverage FLOAT,
		total_leverage FLOAT,
		profit_margin_growth FLOAT,
		return_on_equity_growth FLOAT,
		debt_coverage_growth FLOAT,
		current_leverage_growth FLOAT,
		total_leverage_growth FLOAT,
		revenue_growth FLOAT,
		net_income_growth FLOAT,
		long_term_asset_growth FLOAT,
		equity_growth FLOAT)"""

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





def addReportSuccess(dbc, cursor, data):
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





def reportExists(dbc, cursor, filename):
	try: 
		cursor.execute("SELECT COUNT(*) FROM reports WHERE filename = %s", [filename])
		dbc.commit()
		result  = cursor.fetchall()
		exists  = result[0][0]
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		errors  = str(e)
		success = False

	return {'success': success, 'exists': exists, 'errors': errors}





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



def getUnscoredReports(dbc, cursor):
	try: 
		cursor.execute("SELECT cik, release_date FROM reports WHERE profit_margin IS NULL LIMIT 10")
		dbc.commit()
		result  = cursor.fetchall()
		data = []
		for row in result:
			data.append({'cik': row[0], 'release_date': row[1]});
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)

	return {'success': success, 'data': data, 'errors': errors}







def getReports(dbc, cursor, cik, release_date):
	date = release_date.strftime('%Y-%m-%d')
	query = "SELECT * FROM reports WHERE cik = %s AND release_date <= %s ORDER BY release_date DESC LIMIT 20"
	try: 
		cursor.execute(query, [cik, date])
		dbc.commit()
		result  = cursor.fetchall()
		desc    = cursor.description
		for line in desc:
			print(line[0])
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)

	return {'success': success, 'errors': errors}





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
	query      = "SELECT * FROM reports WHERE cik = %s AND release_date <= %s AND success = 1 ORDER BY release_date DESC LIMIT %s"
	date       = release_date.strftime('%Y-%m-%d')
	parameters = [cik, date, n]
	return dbRead(dbc, cursor, query, parameters)



