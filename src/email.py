import smtplib
from email.message import EmailMessage


class EmailSender():

    def __init__(self, config):
        self.sender = config['GMAIL_SENDER']
        self.password = config['GMAIL_PASSWORD']
        self.hostname = config['HOSTNAME']

    def send(self, to, subject, text, html):
        msg = EmailMessage()
        msg.set_content(text)
        msg.add_alternative(html, subtype='html')
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = to

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(self.sender, self.password)

        server.send_message(msg)

        server.quit()

    def recover_pass(self, url, user):
        a_url = '<a href="' + url + '">Восстановить пароль</a>'

        hello_text = 'Привет, ' + user.visible_name
        recover_text = \
            'Кто-то запросил восстановление пароля для вашего аккаунта. ' + \
            'Ссылка для установки нового пароля: '

        text = hello_text + '\n' + recover_text + url
        html = '<p>' + hello_text + '</p>' + \
            '<p>' + recover_text + '</p>' + \
            a_url

        self.send(user.email, 'Восстановление пароля', text, html)
