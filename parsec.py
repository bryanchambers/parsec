import multiprocessing
import os
import requests
import json
import time
from datetime import datetime



def get_index(year, qtr):
    base_url = "https://www.sec.gov/Archives/edgar/full-index/"
    full_url = base_url + str(year) + "/QTR" + str(qtr) + "/form.idx"
    response = requests.get(full_url)
    return response.text



def save_index(year, qtr, index):
    filename = 'index-' + str(year) + 'q' + str(qtr) + '.json'

    with open('index/' + filename, 'w') as file:
        json.dump(index, file)
        file.close()



def load_index(year, qtr):
    filename = 'index-' + str(year) + 'q' + str(qtr) + '.json'

    try:
        with open('index/' + filename, 'r') as file:
            index = json.load(file)
            file.close()
            return index

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
    try: return requests.get('https://www.sec.gov/Archives/' + filename).text
    except MemoryError:
        print('Report too big [' + filename + ']')



def load_triggers():
    with open('triggers.json') as file:
        triggers = json.load(file)
        file.close()
        return triggers



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
    if not r: return False

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



def get_ratios(data):
    equity = data['total_equity'] if data['total_equity'] else data['total_assets'] - data['total_liabilities']
    total_liabilities = data['total_liabilities'] if data['total_liabilities'] else data['total_liabilities_and_equity'] - equity

    output = {
        'profit_margin':    calc_ratio(data['net_income'], data['revenue']),
        'return_on_equity': calc_ratio(data['net_income'], equity),
        'debt_coverage':    calc_ratio(data['net_income'], data['current_liabilities']),
        'current_leverage': calc_ratio(data['current_assets'], data['current_liabilities']),
        'total_leverage':   calc_ratio(data['total_assets'], total_liabilities)
    }

    for metric in output:
        output[metric] = round(output[metric], 5)

    return output



def calc_ratio(n, d):
    max = 1000
    
    if d == 0:
        return max if n > 0 else 0
    else:
        ratio = float(n) / d
        if   ratio < 0:   return 0
        elif ratio > max: return max
        else: return round(ratio, 5)



def parse_report(cik, info, triggers, year):
    report = get_report(info['file'])

    results = {}
    for metric in triggers:
        results[metric] = parse_metric(report, triggers[metric], year)

    filename = 'results-' + str(cik) + '-' + info['date'] + '.json'

    with open('results/' + filename, 'w') as file:
        json.dump(results, file)
        file.close()



def load_results(cik, date):
    filename = 'results-' + str(cik) + '-' + date + '.json'

    for i in range(10):
        try:
            with open('results/' + filename, 'r') as file:
                results = json.load(file)
                file.close()
                os.remove('results/' + filename)
                return results

        except FileNotFoundError: pass
        time.sleep(0.01)
    
    return False



def parse_quarter(year, qtr, triggers):
    index = load_index(year, qtr)
    total = len(index)

    parsed = 0

    for cik in index:
        update_status(year, qtr, parsed, total)
        if 'metrics' not in index[cik]:
            parse = multiprocessing.Process(target=parse_report, args=(cik, index[cik], triggers, year))
            parse.start()
            parse.join()

            results = load_results(cik, index[cik]['date'])
            parsed  = parsed + 1

            if report_is_valid(results):
                index[cik]['metrics'] = results
                index[cik]['ratios']  = get_ratios(results)
            else:
                index[cik]['metrics'] = False

    save_index(year, qtr, index)



def parse_year(year, triggers):
    for qtr in range(4):
        parse = multiprocessing.Process(target=parse_quarter, args=(year, qtr + 1, triggers))
        parse.start()
        parse.join()



def update_status(year, qtr, parsed, total):
    timestamp = datetime.strftime(datetime.now(), '%d %b %I:%M%p')
    fraction  = ' ' + str(parsed) + '/' + str(total)
    percent   = ' (' + str(round((parsed / total) * 100, 1)) + '%)'

    with open('status.txt', 'w') as file:
        file.write('[' + timestamp + '] ' + str(year) + 'q' + str(qtr) + ' Parsed' + fraction + percent + '\n')



parse_year(2020, load_triggers())
