import requests
import json





def get_index(year, qtr):
    base_url = "https://www.sec.gov/Archives/edgar/full-index/"
    full_url = base_url + str(year) + "/QTR" + str(qtr) + "/form.idx"

    data  = requests.get(full_url).text
    lines = data.splitlines()
    index = {}

    for line in lines:
        if line[:5] == '10-Q ':
            line = line.split('  ')

            row = []
            for text in line:
                text = text.strip()
                
                if text:
                    row.append(text)

            index[row[2]] = { 'name': row[1], 'date': row[3], 'file': row[4] }

    return index





def get_report(filename):
    return requests.get('https://www.sec.gov/Archives/' + filename).text





def load_triggers():
    with open('triggers.json') as file:
        return json.load(file)





def get_snippet(page, trigger, start):
    i = start
    n = len(trigger)

    while i >= 0:
        i = page.find(trigger, i + 1)

        if i >= 0:
            snip = page[i - 50 : i + 5000]
            if not extra_text_before(snip[:50]) and not extra_text_after(snip[50 + n : 100 + n]):
                return snip[50:], i + 1
    return False, i





def extra_text_before(snip):
    j = snip.rfind('>')

    text = snip[j + 1:] if j >= 0 else snip
    text = text.strip()

    if text:
        text = remove_whitespace(text)
    return True if text else False





def extra_text_after(snip):
    j = snip.find('<')

    text = snip[:j] if j >= 0 else snip
    text = text.strip()

    if text:
        text = remove_whitespace(text)
    return True if text else False





def remove_whitespace(text):
    text = ''.join(text.split())

    for char in ['&nbsp;', '&#160;']:
        text.replace(char, '')
    return text





def parse_value(snip, year):
    value = False
    tries = 0

    while not value and tries < 100:
        i = snip.find('>')
        if i > -1:
            snip = snip[i + 1:]

        j = snip.find('<')
        if j > -1:
            text = snip[:j].strip()
        else:
            text = snip.strip()

        if len(text) > 0:
            for char in ['<', '>', '$', '(', ')', ',', '&nbsp;', '&#160;']:
                text = text.replace(char, '')

            x = text.find('.')
            if x > -1:
                text = text[:x]

            try:
                value = int(text)
            except ValueError:
                pass

            if value > -1 and value < 5:
                value = False

            if value > year - 3 and value < year + 3:
                value = False

        tries = tries + 1
    return value





def parse_metric(page, triggers, year):
    for trigger in triggers:
        start = 0
        snip  = True
        value = False

        while snip and not value:
            snip, start = get_snippet(page, trigger, start)

            if snip:
                value = parse_value(snip, year)
                if value:
                    return value

    return False





triggers = load_triggers()
index    = get_index(2018, 2)

for cik in index:
    file   = index[cik]['file']
    report = get_report(file)

    print('-' * 35)
    print('Name'.ljust(22) + ': ' + index[cik]['name'])
    print('CIK'.ljust(22)  + ': ' + cik)
    print('Date'.ljust(22) + ': ' + index[cik]['date'])
    print('')

    for metric in triggers:
        result = parse_metric(report, triggers[metric], 2018)
        if not result:
            print(metric.ljust(22) + ': ' + str(result))
    print('-' * 35 + '\n\n')
