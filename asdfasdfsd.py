import requests



def findReport(words, report):
	if len(words) > 0:
		if words[0] == "10-" + report.upper():
			return True
		else:
			return False


def findCompany(words, company):
	flag = False
	for i in range(0, len(words) - 1):
		if company in words[i]:
			print words[i]
			flag = True
	return flag


def printFilename(words):
	filename = words[len(words) - 1]
	if ".txt" in filename:
		print filename
		return filename


def findFile(lines):
	company = raw_input("Company: ")
	report  = raw_input("Report: ")

	if company != "x" and report != "x":
		for i in range(0, len(lines) - 1):
			words = lines[i].split()
			if findReport(words, report) == True:
				if findCompany(words, company) == True:
					return printFilename(words)
	else:
		return False




print ""
print "Search SEC Index"
print "****************"
print ""

base_url = "https://www.sec.gov/Archives/edgar/full-index/"
year     = raw_input("Year: ")
qtr      = raw_input("Quarter: ")
full_url = base_url + year + "/QTR" + qtr + "/form.idx"

print ""
print "Downloading index..."
index = requests.get(full_url).content
lines = index.split('\n')
print "IDX " + year + " Q" + qtr + " downloaded"
print ""

filename = findFile(lines)
print "https://www.sec.gov/Archives/" + filename