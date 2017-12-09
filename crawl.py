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
info['start']   = datetime.datetime.now()
info['valid']   = 0
info['total']   = 0
info['skipped'] = 0
info['caught']  = 0

completed = db.countReports(dbc, cursor)
print str(completed['count']) + ' Existing Reports'
print ''
startYear = int(raw_input('Start Year: '))
endYear = int(raw_input('  End Year: '))

print("Success | Total | Percent | perDay | Skipped |  Caught |      CIK |    Date    | Status")


for year in range(startYear, endYear - 1, -1):
	for qtr in range(4, 0, -1):
		index = parsec.getIndex(year, qtr)
		reportList = db.getCompletedReportList(dbc, cursor, year, qtr)

		for report in index:
			info['cik']  = report['cik']
			info['date'] = report['date']
			
			if(report['filename'] not in reportList['data']):
				reportExists = db.reportExists(dbc, cursor, report['filename'])
				if(not reportExists['data']):
					chk_company = db.companyExists(dbc, cursor, report['cik'])
					if not chk_company['exists'] and chk_company['success']:
						db.addCompany(dbc, cursor, report)

					output = parsec.parsec(report['filename'], info)
					info['total'] += 1
					
					if output['success']:
						data = db.prepData(report, output)
						db.addReportSuccess(dbc, cursor, data)
						info['valid'] += 1
						parsec.updateStatus(info, 'Success!')
					else:
						db.addReportFail(dbc, cursor, report)
						parsec.updateStatus(info, 'Failed')
				else: info['caught'] += 1
			else: 
				info['skipped'] += 1
				parsec.updateStatus(info, 'Report already exists')
