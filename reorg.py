import json, pathlib
from datetime import datetime
from notify   import email



def get_path():
    return str(pathlib.Path(__file__).parent.absolute()) + '/'



def load_json_file(filename):
    with open(get_path() + filename + '.json', 'r') as file:
        return json.load(file)



def save_json_file(filename, data):
    with open(get_path() + filename + '.json', 'w') as file:
        json.dump(data, file)



def get_current_year():
    now = datetime.now()
    return now.year



def add_special_metrics(m):
    m['equity'] = m['total_equity'] if m['total_equity'] else m['total_assets'] - m['total_liabilities']
    m['long_term_assets'] = m['total_assets'] - m['current_assets']
    return m



def get_reports_by_cik():
    reports = {}

    for year in range(2000, get_current_year() + 1):
        for qtr in range(1, 5):
            filename = 'index-' + str(year) + 'q' + str(qtr)

            try: index = load_json_file('index/' + filename)
            except FileNotFoundError: index = False

            if index:
                for cik in index:
                    date = index[cik]['date']

                    if 'ratios' in index[cik] and index[cik]['ratios']:
                        if cik not in reports:
                            reports[cik] = {}

                        reports[cik][date] = {
                            'metrics': add_special_metrics(index[cik]['metrics']),
                            'ratios':  index[cik]['ratios']
                        }

    return reports



def save_reports_by_cik(reports):
    n = 0 # New reports added
    c = 0 # Existing reports changed

    for cik in reports:
        filename = 'reports-' + str(cik)

        try: company = load_json_file('reports/' + filename)
        except FileNotFoundError: company = {}

        for date in reports[cik]:
            if date not in company:
                company[date] = reports[cik][date]
                n = n + 1

            elif not reports_match(company[date], reports[cik][date]):
                company[date] = reports[cik][date]
                c = c + 1

        save_json_file('reports/' + filename, company)

    return n, c



def reports_match(old, new):
    if not old['metrics'] and not new['metrics']:
        return True

    for metric in old['metrics']:
        if metric not in ['equity', 'long_term_assets']:
            if metric not in new['metrics'] or new['metrics'][metric] != old['metrics'][metric]:
                return False

    for metric in new['metrics']:
        if metric not in ['equity', 'long_term_assets']:
            if metric not in old['metrics'] or new['metrics'][metric] != old['metrics'][metric]:
                return False

    return True



def send_results(n, c):
    subject = 'Parsec Reports Organized'

    msg = str(n) + ' New, ' + str(c) + ' Updated'
    email('bryches@gmail.com', subject, msg)



n, c = save_reports_by_cik(get_reports_by_cik())
send_results(n, c)