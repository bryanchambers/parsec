import requests
import bs4
import re
import tabulate
import string
import random
import operator
import datetime
import MySQLdb

from getIndex   import getIndex
from findTable  import findTable
from cleanTable import cleanTable


print ""
print "Downloading index"
index = getIndex(requests, '2010', '1')
print "Reports available"
print len(index)

base_url = "https://www.sec.gov/Archives/"

print ""
report_start = int(raw_input("Starting report index? "))
report_end   = int(raw_input("Ending report index? "))
print ""

db = MySQLdb.connect("localhost","root","atlas","parsec" )
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS marks_income(id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(200), count INT, report INT)")

t0 = datetime.datetime.now()
print "Started"
print t0
print ""

for r in range(report_start, report_end):
	report = index[r]
	filename = report["filename"]

	page = requests.get(base_url + filename).content
	soup = bs4.BeautifulSoup(page, "lxml")

	tables = soup.findAll("table")


	marks = []
	for table in tables: 
		rows = table.findAll("tr")

		if len(rows) > 5:
			for row in rows:
				td = row.find("td")
				if td:
					name = td.text
					if len(name) > 3 and len(name) < 50:
						#if "asset" in name or "liabilit" in name:
						if 'income' in name or 'profit' in name or 'loss' in name:
						#if 'revenue' in name or 'sales' in name:
						#if 'cash' in name:
							name = name.strip(string.whitespace).strip(u'\xa0').lower()
							name = name.encode('ascii', 'ignore')
							name = " ".join(name.split())
							name = name.replace("'", "")
							marks.append(name)

	for mark in set(marks):
		count = marks.count(mark)
		cursor.execute("SELECT id FROM marks_income WHERE name = '%s'" % mark)
		if cursor.fetchone():
			cursor.execute("""UPDATE marks_income SET count = count + %s, report = %s WHERE name = %s""", (count, r, mark))
		else:
			cursor.execute("""INSERT INTO marks_income(name, count, report) VALUES(%s, %s, %s)""", (mark, count, r))
		db.commit()


t1 = datetime.datetime.now()
print "Finished"
print t1
print ""

print "Runtime"
print t1 - t0
print ""
