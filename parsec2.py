import requests
import json
from datetime import datetime






def get_index(year, qtr):
    base_url = "https://www.sec.gov/Archives/edgar/full-index/"
    full_url = base_url + str(year) + "/QTR" + str(qtr) + "/form.idx"

    return requests.get(full_url).text



def save_index(year, qtr, index):
    filename = 'index-' + str(year) + 'q' + str(qtr) + '.json'

    with open('index/' + filename, 'w') as file:
        json.dump(index, file)



def load_index(year, qtr):
    filename = 'index-' + str(year) + 'q' + str(qtr) + '.json'

    try:
        with open('index/' + filename, 'r') as file:
            return json.load(file)

    except FileNotFoundError:
        index = parse_index(get_index(year, qtr))
        save_index(year, qtr, index)
        return index



def parse_index(data):
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





def save_report(info, report):
    name = info['name']
    
    for char in ['.', '/', '-', ',', '&', '(', ')']:
        name = name.replace(char, '')

    filename = name.lower().replace(' ', '-') + '-' + info['date'] + '.html'

    a = report.find('<html>')
    b = report.find('<HTML>')

    if   a > -1 and b > -1: i = min(a, b)
    elif a > -1 or  b > -1: i = a if a > -1 else b
    else: i = False

    opening_tag = report[i:i + 6] if i else False
    closing_tag = '</html>' if opening_tag == '<html>' else '</HTML>'

    j = report.find(closing_tag, i) if i else False

    if i and j:
        with open('reports/html/' + filename, 'w') as file:
            file.write(report[i:j + 7])






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

    while not value and tries < 50:
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

        while snip and not value and start < 500000:
            snip, start = get_snippet(page, trigger, start)

            if snip:
                value = parse_value(snip, year)
                if value:
                    return value

    return False





def report_is_valid(results):
    r = results

    if (r['revenue']
        and r['net_income']
        and r['current_assets']
        and r['total_assets']
        and r['current_liabilities']
    ):
        if (r['total_liabilities']
            or (r['total_equity'] and r['total_liabilities_and_equity'])
        ):
            return True

    return False






def calc_ratios(data):
    equity = data['total_equity'] if data['total_equity'] else data['total_assets'] - data['total_liabilities']

    total_liabilities = data['total_liabilities'] if data['total_liabilities'] else data['total_liabilities_and_equity'] - equity

    output = {
        'profit_margin':    float(data['net_income'])     / data['revenue'],
        'return_on_equity': float(data['net_income'])     / equity,
        'debt_coverage':    float(data['net_income'])     / data['current_liabilities'],
        'current_leverage': float(data['current_assets']) / data['current_liabilities'],
        'total_leverage':   float(data['total_assets'])   / total_liabilities
    }

    for metric in output:
        output[metric] = round(output[metric], 5)

    return output










yr = 2018
triggers = load_triggers()
index = load_index(yr, 2)


for cik in index:
    if 'metrics' not in index[cik]:
        report = get_report(index[cik]['file'])
        name   = index[cik]['name']
        date   = index[cik]['date']

        results = {}
        for metric in triggers:
            results[metric] = parse_metric(report, triggers[metric], yr)

        if report_is_valid(results):
            index[cik]['metrics'] = results
            index[cik]['ratios']  = calc_ratios(results)
        else:
            index[cik]['metrics'] = False

save_index(yr, 2, index)