import requests
from urllib.parse import urlencode

def send_to_trello(config, text):
  if not config['TRELLO_KEY'] or not config['TRELLO_TOKEN']:
    return False

  query = urlencode({
    'key': config['TRELLO_KEY'],
    'token': config['TRELLO_TOKEN'],
    'idList': config['TRELLO_LIST_ID']
  })

  req = requests.post('https://api.trello.com/1/cards?' + query, data={
    'name': text[:128] + ('...' if len(text) > 128 else ''),
    'desc': text
  })

  return req.status_code == 200
