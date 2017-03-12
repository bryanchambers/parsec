def findElement(soup):
	cnt_font = len(soup.findAll("font"))
	cnt_p    = len(soup.findAll("p"))
	if cnt_font > cnt_p:
		element = "font"
	else:
		element = "p"
	return element