def findTable(soup, element, title):
	mark_list = soup.findAll(element)
	for i in range(0, len(mark_list) - 1):
		if "consolidated balance sheets" in mark_list[i].text.lower():
			units = mark_list[i].findNext(element).text.lower()
			if "thousands" in units or "millions" in units:
				mark = mark_list[i]
	return mark