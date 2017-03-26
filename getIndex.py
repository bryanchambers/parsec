import requests

def getIndex(year, qtr):
	base_url = "https://www.sec.gov/Archives/edgar/full-index/"
	full_url = base_url + year + "/QTR" + qtr + "/form.idx"
	
	data  = requests.get(full_url).content
	lines = data.split('\n')

	index = []
	for i in range(len(lines)):
		items = lines[i].split()
		if len(items) > 0 and items[0] == "10-Q":
			last = len(items) - 1

			company = ""
			for n in range(1, last - 3):
				company += " " + items[n]
			company = company[1:].lower()

			cik      = items[last - 2]
			date     = items[last - 1]
			filename = items[last]
			
			row = {"company": company, "cik": cik, "date": date, "filename": filename}
			index.append(row)
	return index
