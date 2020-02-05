import json

year = 2018
qtr  = 4

def percent(value):
    percent = round((value / total) * 100, 1)
    return ('(' + str(percent) + '%)').rjust(8)

with open('index/' + 'index-' + str(year) + 'q' + str(qtr) + '.json', 'r') as file:
    index = json.load(file)

total   = len(index)
tried   = 0
success = 0

for cik in index:
    if 'metrics' in index[cik]:
        tried = tried + 1

        if index[cik]['metrics']:
            success = success + 1

print('')
print(str(year) + ' Q' + str(qtr))
print('-' * 25)
print(str(total).rjust(5)   + ' Reports')
print(str(tried).rjust(5)   + ' Attempted  ' + percent(tried))
print(str(success).rjust(5) + ' Successful ' + percent(success))
print('')