import requests
import bs4
import re
import tabulate
import string
import random

from getIndex import getIndex
from findElement import findElement
from findTable import findTable
from cleanTable import cleanTable


base_url = "https://www.sec.gov/Archives/"
#filename = "edgar/data/1034670/0001193125-16-568223.txt" #Autoliv
#filename = "edgar/data/1447599/0001447599-16-000050.txt" #Fitbit
#filename = "edgar/data/1418121/0001185185-16-004411.txt" #Apple




index = getIndex(requests, '2016', '2')




count_valid_reports = 0
for z in range(0, 100):
	print z
	report = index[random.randint(0, len(index) - 1)]
	#print report["cik"]
	#print report["date"]

	filename = report["filename"]
	page = requests.get(base_url + filename).content
	soup = bs4.BeautifulSoup(page, "lxml")


	query = "consolidated balance sheets"
	tables = findTable(re, soup)

	t = 0
	count_valid = 0
	while t < len(tables) and count_valid < 4: 
		rows = cleanTable(tables[t]["table"], string)


		data = {"total current assets": 0, "total assets": 0, "total current liabilities": 0, "total liabilities": 0}

		for row in rows:
			if len(row) > 1:
				name = row[0].lower()
				for item in data.keys():
					if item == name:
						data[item] = row[1]

		count_valid = 0
		for val in data.values():
			if val != 0:
				count_valid += 1

		if count_valid == 4:
			print tables[t]["order"]
			print data
			print ""
			count_valid_reports += 1

		t += 1

print ""
print count_valid_reports