import requests
import bs4
import json
import re
import string
import datetime





def getIndex(year, qtr):
	base_url = "https://www.sec.gov/Archives/edgar/full-index/"
	full_url = base_url + str(year) + "/QTR" + str(qtr) + "/form.idx"
	
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
			if company.endswith(','): company = company[:-1]

			cik      = items[last - 2]
			date     = items[last - 1]
			filename = items[last]
			
			row = {"company": company, "cik": cik, "date": date, "filename": filename}
			index.append(row)
	return index





def cleanText(dirty):
	if isinstance(dirty, basestring):
		clean = dirty.strip(string.whitespace).strip(u'\xa0').encode('ascii', 'ignore').replace("'", "").lower()
		clean = " ".join(clean.split())
		if len(clean) > 0: return clean
		else: return False
	else: return False





def cleanNumber(dirty):
	if isinstance(dirty, basestring):
		dirty = dirty.replace(',', '')
		clean = re.search('\(?\d+\.?\d*\)?', dirty)
		if clean:
			clean = clean.group(0)
			number = re.search('\d+\.?\d*', clean)
			if number:
				number = float(number.group(0))
				if clean[0] == '(' or clean[-1] == ')': number *= -1
				return number
		else: return False
	else: return False





def matchHeader(text, data):
	for header in data:
		for accepted in header['accepted']:
			if text == accepted:
				return header['header']
	return False





def compareValues(v1, v2, t1, t2):
	if (v1 - v2) >= t1 and (v1 / (float(v2) + 0.1)) >= t2: return True
	else: return False





def findUnits(page):
	cnt_thou = len(re.findall('thousands', page, re.IGNORECASE))
	cnt_mill = len(re.findall('millions', page, re.IGNORECASE))

	if   compareValues(cnt_thou, cnt_mill, 3, 3): return 1
	elif compareValues(cnt_mill, cnt_thou, 3, 3): return 1000
	elif (cnt_thou + cnt_mill) <= 3:       return 0.001
	else: return False





def getRows(page, soup):
	tables = soup.findAll('table')
	if tables:
		all_rows = []
		for table in tables:
			rows = table.findAll('tr')
			if not rows:
				rows = table.text.split('\n')
			all_rows.extend(rows)
		return all_rows
	else:
		return page.split('\n')





def findDateOrder(row):
	dates = []
	
	if hasattr(row, 'findAll'):
		cells = row.findAll('td')
		if not cells: 
			cells = row.text.split('   ')
	else: cells = row.split('   ')
	
	if cells:
		if len(cells) > 1:
			for cell in cells:
				if hasattr(cell, 'text'): text = cleanText(cell.text)
				else: text = cleanText(cell)
				if text:
					date_str = re.search('\w+ \d\d?, \d\d\d\d', text)
					if not date_str:
						date_str = re.search('\d\d\d\d', text)
					if date_str:
						try: date = datetime.datetime.strptime(date_str.group(0), '%B %d, %Y')
						except ValueError:
							try: date = datetime.datetime.strptime(date_str.group(0), '%Y')
							except ValueError: date = False
						if date: 
							date_min = datetime.datetime.strptime('1990', '%Y')
							date_max = datetime.datetime.today() + datetime.timedelta(weeks=52)
							if date > date_min and date < date_max:
								dates.append(date)
		if len(dates) == 2 or len(dates) == 4:
			if dates[0] > dates[1]: return 'std'
			else: return 'rev'
		else: return False
	else: return False





def setDateOrder(rows):
	cnt_std = 0
	cnt_rev = 0
	for row in rows:
		order = findDateOrder(row)
		if order:
			if   order == 'std': cnt_std += 1
			elif order == 'rev': cnt_rev += 1

	if   compareValues(cnt_std, cnt_rev, 2, 5): return 'std'
	elif compareValues(cnt_rev, cnt_std, 2, 5): return 'rev'
	else: return False





def parseRow(row, data, units, date_order):
	values = []
	
	if hasattr(row, 'findAll'):
		cells = row.findAll('td')
		if not cells: 
			cells = row.text.split('   ')
	else: cells = row.split('   ')

	if cells:
		if len(cells) > 1:
			if hasattr(cells[0], 'text'):
				text = cleanText(cells[0].text)
			else: text = cleanText(cells[0])

			header = matchHeader(text, data)
			if header:
				for i in range(1, len(cells)):
					if hasattr(cells[i], 'text'):
						value = cleanNumber(cells[i].text)
					else: value = cleanNumber(cells[i])
					if value: values.append(int(value * units))
				
				if len(values) == 2 or len(values) == 4:
					if   date_order == 'std': output = values[0::2]
					elif date_order == 'rev': output = values[1::2]
					else: output = values[0::2]

					if output:
						if len(output) == 1: output = output[0]
						return {'header': header, 'values': output}
					else: return False
				else: return False 
			else: return False
		else: return False
	else: return False





def resetValues(data):
	for i in range(len(data)):
		for j in range(len(data[i]['values'])):
			data[i]['values'][j] = 0
	return data





def valuesFilled(data):
	flag    = True
	missing = []

	for item in data:
		if not item['optional']:
			if item['values'] == 0: 
				flag = False
				missing.append(item['header'])
	return {'success': flag, 'missing': missing}





def parseReportSection(data, rows, units, date_order):
	fails = 0
	done  = False
	for row in rows:
		if not done:
			output = parseRow(row, data, units, date_order)
			if output: 
				for i in range(len(data)):
					if data[i]['header'] == output['header']:
							if data[i]['values'] == 0: data[i]['values'] = output['values']
							#if valuesFilled(data): done = True
			else: fails += 1
			#if fails > 50: data = resetValues(data)
	return data





def slimData(data):
	output = []
	for item in data:
		row = {'header': item['header'], 'values': item['values']}
		output.append(row)
	return output





def parseReport(rows, units, date_order):
	with open('headers.json') as headers_json:
		headers = json.load(headers_json)
	output  = []
	errors  = []
	success = True
	
	for section in headers:
		parsed = parseReportSection(section['data'], rows, units, date_order)
		validate = valuesFilled(parsed)
		if validate['success']:
			output += slimData(parsed)
		else: 
			success = False
			error   = {'*section': section['table'], 'missing': validate['missing']}
			errors.append(error)
	return {'success': success, 'output': output, 'errors': errors}





def parsec(filename):
	success = False
	errors  = []
	output  = []

	base_url = 'https://www.sec.gov/Archives/'
	
	page = requests.get(base_url + filename).content
	print 'Downloaded'
	
	soup = bs4.BeautifulSoup(page, "lxml")
	print 'Soupy'

	units = findUnits(page)
	if units:
		print 'Units ' + str(int(units * 1000))
		
		rows = getRows(page, soup)
		try: print str(len(rows)) + ' Rows'
		except TypeError: print 'Blank?'
		
		date_order = setDateOrder(rows)
		if date_order:
			if date_order == 'std': print 'Standard dates'
			else: print 'Reverse dates' 

			print 'Parsing'
			data = parseReport(rows, units, date_order)
			if data['success']:
				print 'Parse complete'
				success = True
				output  = data['output'] 
			else: 
				errors.append('Report parse failure')
				errors.append(data['errors'])
				print 'Parse failure'
		else: 
			errors.append('Date order not found') 
			print 'Date order not found'
	else: 
		errors.append('Units not found')
		print 'Units not found'

	return {'success': success, 'output': output, 'errors': errors}