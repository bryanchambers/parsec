import datetime
import db
import parsec

dbc    = db.dbConnect('localhost', 'root', 'atlas', 'parsec')
cursor = db.getCursor(dbc)

db.createTable(cursor, 'reports')
db.createTable(cursor, 'companies')

print ""
print "Parsec SEC Crawler"
print "******************"
print ""

count_good  = 0
count_total = 0

for year in range(2016, 1994, -1):
	for qtr in range(4, 0, -1):
		print 'Downloading index for ' + str(year) + ' Q' + str(qtr)
		index = parsec.getIndex(year, qtr)
		print 'Index downloaded'
		
		for report in index:
			filename = report['filename']
			print ""
			print report['company']
			print str(year) + ' Q' + str(qtr)
			print filename
			
			chk_company = db.companyExists(dbc, cursor, report['cik'])
			if not chk_company['exists'] and chk_company['success']:
				db.addCompany(dbc, cursor, report)

			chk_report = db.reportExists(dbc, cursor, filename)
			if not chk_report['exists'] and chk_report['success']:
				print datetime.datetime.now().strftime("%d %b %I:%M:%S%p")
				output = parsec.parsec(filename)
				if output['success']:
					data = db.prepData(report, output)
					print 'Data prepped'
					db.addReportSuccess(dbc, cursor, data)
					count_good += 1
				else:
					db.addReportFail(dbc, cursor, report)
				count_total += 1
				success_rate = int((float(count_good) / count_total) * 100)
				print datetime.datetime.now().strftime("%d %b %I:%M:%S%p")
				print 'Success rate ' + str(count_good) + '/' + str(count_total) + ' ' + str(success_rate) + '%'
			else: print 'Already there'
