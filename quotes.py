import requests
import bs4

page = requests.get("http://www.nasdaq.com/symbol/aapl").content
soup = bs4.BeautifulSoup(page, "lxml")

pe = soup.find('a', id='pe_ratio').parent.findNext('td').getText()

price = soup.find('div', id='qwidget_lastsale').getText()
if '$' in price: price = round(float(price[1:]), 2)

print(pe)
print(price)
