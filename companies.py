import json, pathlib
from notify import email



def get_path():
    return str(pathlib.Path(__file__).parent.absolute()) + '/'



def load_json_file(filename):
    with open(get_path() + filename + '.json', 'r') as file:
        return json.load(file)



def save_json_file(filename, data):
    with open(get_path() + filename + '.json', 'w') as file:
        json.dump(data, file)



def update_companies():
    try: companies = load_json_file('info/companies')
    except FileNotFoundError: companies = {}

    n = 0

    for year in range(2010, 2020):
        for qtr in range(1, 5):
            filename = 'index-' + str(year) + 'q' + str(qtr)

            try: index = load_json_file('index/' + filename)
            except FileNotFoundError: index = False

            if index:
                for cik in index:
                    if cik not in companies:
                        n = n + 1
                        companies[cik] = { 'name': index[cik]['name'] } 

    save_json_file('info/companies', companies)
    send_results(n)



def send_results(n):
    subject = 'Parsec Companies Updated'

    msg = str(n) + ' Added'
    email('bryches@gmail.com', subject, msg)



update_companies()