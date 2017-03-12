import requests
import bs4
import re
import tabulate
import string

from findElement import findElement
from findTable import findTable
from getTable import getTable


base_url = "https://www.sec.gov/Archives/"
#filename = "edgar/data/1034670/0001193125-16-568223.txt" #Autoliv
filename = "edgar/data/1447599/0001447599-16-000050.txt" #Fitbit
#filename = "edgar/data/1418121/0001185185-16-004411.txt" #Apple


page = requests.get(base_url + filename).content
soup = bs4.BeautifulSoup(page, "lxml")


element = findElement(soup)
mark = findTable(soup, element, "consolidated balance sheets")
rows = getTable(mark, string)






print tabulate.tabulate(rows)
