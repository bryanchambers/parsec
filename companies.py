import json, smtplib, ssl, pathlib
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