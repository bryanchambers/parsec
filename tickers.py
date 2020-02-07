import json, requests, difflib, csv, smtplib, ssl, pathlib
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText



def get_path():
    return str(pathlib.Path(__file__).parent.absolute()) + '/'



def load_json_file(filename):
    with open(get_path() + filename + '.json', 'r') as file:
        return json.load(file)



def save_json_file(filename, data):
    with open(get_path() + filename + '.json', 'w') as file:
        json.dump(data, file)



def email(to, subject, body):
    ses = load_json_file('ses')
    msg = create_email(to, subject, body, ses)
    send_email(to, msg, ses)



def create_email(to, subject, body, ses):
    msg = MIMEMultipart()
    msg['From']    = ses['sender']
    msg['To']      = to
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))
    return msg.as_string()



def send_email(to, msg, ses):
    smtp = smtplib.SMTP(ses['endpoint'], 587)
    smtp.starttls()
    smtp.login(ses['username'], ses['password'])
    smtp.sendmail(ses['sender'], to, msg)
    smtp.quit()



def parse_csv_value(line):
    i = line.find('"')
    text = line[i + 1:]

    j = text.find('"')
    value = text[:j].strip()

    remaining = text[j + 1:]
    return value, remaining



def get_tickers():
    tickers = {}

    for exchange in ['nyse', 'nasdaq']:
        url   = 'http://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=' + exchange + '&render=download'
        res   = requests.get(url)
        file  = res.text
        lines = file.splitlines()

        for line in lines:
            ticker,  remaining = parse_csv_value(line)
            company, remaining = parse_csv_value(remaining)
            company = company.lower()

            if len(company) < 200 and len(ticker) < 20:
                if company not in tickers:
                    tickers[company] = ticker.upper()

    save_json_file('info/tickers', tickers)



def get_name_variations(n):
    v = { n: True }

    for punc in ['.', ',', '/']: 
        name = n.replace(punc, '')
        if name not in v: v[name] = True

    abv = {
        'inc':  'incorporated',
        'co':   'company',
        'corp': 'corporation',
        'ltd':  'limited',
        'llc':   None,
        'lp':    None,
        'nv':    None
    }

    for a in abv:
        full = abv[a]
        base = [a, ' ' + a, a + '.']
        pre  = [',', ', ']

        find = []

        for b in base:
            find.append(b)
            for p in pre: find.append(p + b)

        repl = ['']
        if full: repl.append(full)

        for f in find:
            repl.append(f)
            repl.append(f + '.')

        for f in find: 
            for r in repl: 
                name = n.replace(f, r)
                if name not in v: v[name] = True

    return v



def parse_tickers():
    tickers   = load_json_file('info/tickers')
    companies = load_json_file('info/companies')

    m = 0 # Matches
    n = 0 # New company or ticker
    c = 0 # Ticker changed

    for cik in companies:
        name = companies[cik]['name'].lower()

        for variation in get_name_variations(name):
            if variation in tickers:
                m = m + 1
                ticker = tickers[variation].upper()

                if 'ticker' not in companies[cik]: n = n + 1
                if 'ticker' in companies[cik] and companies[cik]['ticker'] != ticker: c = c + 1
                companies[cik]['ticker'] = ticker
                break
    
    save_json_file('info/companies', companies)
    send_results(len(tickers), m, n, c)



def send_results(total, matches, new, changes):
    subject = 'Parsec Tickers Updated'
    percent = round((matches / float(total)) * 100, 1)

    msg = str(new) + ' New, ' + str(changes) + ' Changes, ' + str(matches) + '/' + str(total) + ' Matched (' + str(percent) + '%)'
    email('bryches@gmail.com', subject, msg)



get_tickers()
parse_tickers()