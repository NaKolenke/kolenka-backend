import requests

class Telegram():
    def __init__(self, config):
        self.bot_token = None
        if 'TELEGRAM_BOT_TOKEN' in config:
            self.bot_token = config['TELEGRAM_BOT_TOKEN']
        if 'TELEGRAM_ADMIN_CHANNEL' in config:
            self.admin_channel_id = config['TELEGRAM_ADMIN_CHANNEL']

    def notify_admin_channel(self, message):
        if self.bot_token:
            self.send_message(self.admin_channel_id, message)

    def send_message(self, id, message):
        requests.post('https://api.telegram.org/bot' + self.bot_token + '/sendMessage', json={
            'chat_id': id,
            'parse_mode': 'html',
            'text': message
        })
