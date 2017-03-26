import datetime
import getIndex
from   parsec import parsec
from   pprint import pprint


index = getIndex.getIndex('2010', '2')

print ""
report_start = int(raw_input("Starting report index? "))
report_end   = int(raw_input("Ending report index? "))
print ""




def orgErrors(errors):
	missing = []
	if len(errors) == 2:
		for err in errors[1]:
			missing += err['missing']
	return missing




cnt_good = 0
cnt_fail = 0
missing  = []

for r in range(report_start, report_end):
	report = index[r]
	filename = report["filename"]
	output = parsec(filename)
	if output['*success']:
		cnt_good += 1
		print "*****Yay!" + datetime.datetime.now().strftime('%d %b %I:%M:%S%p')
		pprint(output['output'])
	else:
		cnt_fail += 1
		print "Fail " + datetime.datetime.now().strftime('%d %b %I:%M:%S%p')
		print output['errors']
		print "https://www.sec.gov/Archives/" + filename
		print ""

print ""
print str(cnt_good) + '/' + str(cnt_good + cnt_fail)
print str(round((float(cnt_good) / float(cnt_fail + 0.1) * 100, 1)) + '%'



