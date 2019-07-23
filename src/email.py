import smtplib
from email.message import EmailMessage


class EmailSender():

    def __init__(self, config):
        self.sender = config['GMAIL_SENDER']
        self.password = config['GMAIL_PASSWORD']
        self.hostname = config['HOSTNAME']

    def send(self, to, subject, text):
        msg = EmailMessage()
        msg.set_content(text)
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = to

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(self.sender, self.password)
        
        server.sendmail(
            self.sender,
            to,
            msg.encode("utf8"))

        server.quit()
