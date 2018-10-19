import db

dbc    = db.dbConnect('localhost', 'root', 'atlas', 'parsec')
cursor = db.getCursor(dbc)

def calc_final_score(health_score, pe_score):
	scores = [health_score, pe_score]
	low    = min(scores)
	high   = max(scores)
	weight = (100 - float(low)) / 20
	return int((high + low * weight) / (weight + 1))

companies = db.get_listed_companies(dbc, cursor)

if companies['success']:
	for company in companies['data']:
		report = db.get_latest_report(dbc, cursor, company['cik'])
		
		if report['success']:
			health_score = report['data'][0]['overall_score']
			
			if health_score is not None and company['pe_score'] is not None:
				final_score = calc_final_score(health_score, company['pe_score'])
				db.save_final_score(dbc, cursor, company['cik'], health_score, final_score)