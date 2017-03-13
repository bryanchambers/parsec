def findTable(re, soup):
	tables = soup.findAll("table")

	output = []
	i = 0
	while i < len(tables) and i < 10:
		count = len(tables[i].findAll(text=re.compile("assets"))) + len(tables[i].findAll(text=re.compile("liabilities")))
		if count > 4:
			output.append({"table": tables[i], "order": i})
		i += 1
	return output