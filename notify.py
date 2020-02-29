import json, smtplib, pathlib
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText



def get_path():
    return str(pathlib.Path(__file__).parent.absolute()) + '/'



def load_json_file(filename):
    with open(get_path() + filename + '.json', 'r') as file:
        return json.load(file)



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