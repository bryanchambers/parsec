query = """CREATE TABLE IF NOT EXISTS reports(
				id INT PRIMARY KEY AUTO_INCREMENT,
				cik INT NOT NULL,
				release_date DATE NOT NULL,
				filename VARCHAR(255) NOT NULL,
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



def addReport(cursor, data):
	query = """INSERT INTO reports(
					cik, release_date, filename,
					net_income, operating_income, gross_income, revenue,
					net_income_ext, operating_income_ext, gross_income_ext, revenue_ext,
					total_assets, total_liabilities, current_assets, current_liabilities,
					operating_cash_flow, investing_cash_flow, financing_cash_flow, starting_cash, ending_cash) 
					VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

	try: 
		cursor.execute(query, data)
		success = True
		errors  = 'None'
	except MySQLdb.Error, e:
		success = False
		errors  = str(e)

	return {'success': success, 'errors': errors}






def prepData(cik, release_date, filename, data):
	d = {}
	for row in data:
		if isinstance(row['values'], int):
			d[row['header']] = row['values']
		elif len(row['values'] == 2):
			d[row['header']] = row['values'][0]
			d[row['header'] + '_ext'] = row['values'][1]

	return (cik, release_date, filename,
			d['net_income'], d['operating_income'], d['gross_income'], d['revenue'],
			d['net_income_ext'], d['operating_income_ext'], d['gross_income_ext'], d['revenue_ext'],
			d['total_assets'], d['total_liabilities'], d['current_assets'], d['current_liabilities'],
			d['operating_cash_flow'], d['investing_cash_flow'], d['financing_cash_flow'], d['starting_cash'], d['ending_cash'])
