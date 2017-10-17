import requests

file = requests.get("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download").content

lines = file.splitlines()

for line in lines:
	values = line.split(",")
	print(values[0])