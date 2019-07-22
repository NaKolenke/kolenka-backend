import smtplib


class EmailSender():

    def __init__(self, config):
        self.sender = config['GMAIL_SENDER']
        self.password = config['GMAIL_PASSWORD']
        self.hostname = config['HOSTNAME']

    def send(self, to, subject, text):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(self.sender, self.password)

        msg = ('From: ' + self.sender + '\r\n' +
               'To: ' + to + '\r\n' +
               'Subject: ' + subject + '\r\n\r\n' +
               text)

        server.sendmail(
            self.sender,
            to,
            msg.encode("utf8"))

        server.quit()
