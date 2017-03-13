def cleanTable(table, string):
	rows = []
	lines = table.findAll("tr")
	for i in range(0, len(lines) - 1):
		row = []
		items = lines[i].findAll("td")
		for j in range(0, len(items) - 1):
			text = items[j].text.strip("$)").strip(u"\xa0").strip(string.whitespace)
			if len(text) > 0:
				row.append(text)
		rows.append(row)
	return rows