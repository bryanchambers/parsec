import datetime
import db
import parsec

dbc    = db.dbConnect('localhost', 'root', 'atlas', 'parsec')
cursor = db.getCursor(dbc)

db.createTable(cursor, 'reports')
db.createTable(cursor, 'companies')

print ''
print ''
print '********** PARSEC **********'
print '****************************'
print ''

valid = 0
total = 0

info = {}
info['start'] = datetime.datetime.now()

completed = db.countReports(dbc, cursor)
print str(completed['count']) + ' Existing Reports'
print ''
print("Success | Total | Percent | perDay | CIK | Date | Status |")

startYear = db.getLastReportYear(dbc, cursor)['year']
endYear   = 1995
for year in range(startYear, endYear, -1):
	for qtr in range(5, 1, -1):
		index = parsec.getIndex(year, qtr)
		reportList = db.getCompletedReportList(dbc, cursor, year, qtr)
		print(reportList)

		for report in index:
			if(report['filename'] not in reportList):
				info['cik']  = report['cik']
				info['date'] = report['date']
				
				chk_company = db.companyExists(dbc, cursor, report['cik'])
				if not chk_company['exists'] and chk_company['success']:
					db.addCompany(dbc, cursor, report)

				info['valid'] = valid;
				info['total'] = total;
				output = parsec.parsec(report['filename'], info)
				
				if output['success']:
					data = db.prepData(report, output)
					db.addReportSuccess(dbc, cursor, data)
					valid += 1
					parsec.updateStatus(info, 'Success!')
				else:
					db.addReportFail(dbc, cursor, report)
					parsec.updateStatus(info, 'Failed')
				
				total += 1
