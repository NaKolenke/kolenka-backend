import requests


class Trello():

    def __init__(self, config):
        self.query = {
            'key': config['TRELLO_KEY'],
            'token': config['TRELLO_TOKEN'],
            'idList': config['TRELLO_LIST_ID']
        }

    def create_card(self, text):
        req = requests.post(
            'https://api.trello.com/1/cards',
            params=self.query,
            data={
                'name': text[:128] + ('...' if len(text) > 128 else ''),
                'desc': text
            })

        return req.status_code == 200
