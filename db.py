import MySQLdb

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
		net_income_ext INT,
		operating_income_ext INT,
		gross_income_ext INT,
		revenue_ext INT,
		total_assets INT,
		total_liabilities INT,
		current_assets INT,
		current_liabilities INT,
		operating_cash_flow INT,
		investing_cash_flow INT,
		financing_cash_flow INT,
		starting_cash INT,
		ending_cash INT)"""

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
			d['net_income_ext'], d['operating_income_ext'], d['gross_income_ext'], d['revenue_ext'],
			d['total_assets'], d['total_liabilities'], d['current_assets'], d['current_liabilities'],
			d['operating_cash_flow'], d['investing_cash_flow'], d['financing_cash_flow'], d['starting_cash'], d['ending_cash'])





def addReportSuccess(dbc, cursor, data):
	query = """INSERT INTO reports(
		cik, release_date, filename, success,
		net_income, operating_income, gross_income, revenue,
		net_income_ext, operating_income_ext, gross_income_ext, revenue_ext,
		total_assets, total_liabilities, current_assets, current_liabilities,
		operating_cash_flow, investing_cash_flow, financing_cash_flow, starting_cash, ending_cash) 
		VALUES(%s, %s, %s, 1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

	try: 
		cursor.execute(query, data)
		dbc.commit()
		success = True
		errors  = 'None'
		print 'Added to db'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)
		print 'Database error during addReportSuccess'
		print errors

	return {'success': success, 'errors': errors}





def addReportFail(dbc, cursor, report):
	query = "INSERT INTO reports(cik, release_date, filename, success) VALUES(%s, %s, %s, 0)"

	try: 
		cursor.execute(query, [report['cik'], report['date'], report['filename']])
		dbc.commit()
		success = True
		errors  = 'None'
		print 'Added to db'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)
		print 'Database error during addReportFail'
		print errors

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
		print 'Database error during reportExists'
		print errors

	return {'success': success, 'exists': exists, 'errors': errors}





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
		print 'Database error during companyExists'
		print errors

	return {'success': success, 'exists': exists, 'errors': errors}





def addCompany(dbc, cursor, report):
	query = "INSERT INTO companies(cik, name) VALUES(%s, %s)"

	try: 
		cursor.execute(query, [report['cik'], report['company']])
		dbc.commit()
		success = True
		errors  = 'None'
		print 'Added new company to db'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)
		print 'Database error during addCompany'
		print errors

	return {'success': success, 'errors': errors}