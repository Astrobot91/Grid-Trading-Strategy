import requests

# bot = 't.me/gridinfobot'
def message(message):
    apiToken = '6866967756:AAFBcjOKa3HnGWNjaqeTH_7DAGkM8n9ybX0'
    chatID = '1134875199'
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage?chat_id={chatID}&text={message}'
    requests.post(apiURL)

