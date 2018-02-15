import requests

file = requests.get("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download").content

lines = file.splitlines()

for line in lines:
	data = line.split(",")
	ticker = data[0].replace('"', '').strip()
	company = data[1].replace('"', '').strip().lower()
	print(company)
	