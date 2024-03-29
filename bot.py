import telebot
import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime

bot = telebot.TeleBot('911305435:AAGXq7c4Qf3tUBbF4-7nZ_vYqmj4LeRaX84')
TOKEN = '911305435:AAGXq7c4Qf3tUBbF4-7nZ_vYqmj4LeRaX84'
def get_menu(selector, date=None):
    URL = 'http://www.kaist.edu/_prog/fodlst/?site_dvs_cd=en'

    if date:
        URL += '&stt_dt=' + date

    response = requests.get(URL)
    html = response.content

    soup = BeautifulSoup(html, 'html.parser')
    elems = soup.select(selector)
    elem = elems[0]
    menu = elem.get_text()

    return menu

def get_photo():
    URL = 'https://dog.ceo/api/breeds/image/random'

    response = requests.get(URL)
    html = response.content

    soup = str(BeautifulSoup(html, 'html.parser'))

    return soup

def get_time():
    URL = 'http://www.kaist.edu/html/en/kaist/kaist_010701.html'

    response = requests.get(URL)
    html = response.content

    soup = BeautifulSoup(html, 'html.parser')
    table = str(soup.find_all(summary="OLEV On-campus Shuttle"))
    schedule = re.findall(r'<td rowspan="2">\s*(.*?)\s*\</td>', table)

    return schedule

def get_events():
    URL = 'https://www.kaist.ac.kr/html/en/index.html'

    response = requests.get(URL)
    html = response.content

    soup = BeautifulSoup(html, 'html.parser')
    info = str(soup.find_all("div", {"class": "descpt"}))
    dates = re.findall(r'<li><em>\s*(.*?)\s*\</em>', info)
    events = re.findall(r'<li>\s*(.*?)\s*\</li>', info)
    event = info
  #  for i in range(len(dates)):
 #       event[i] = dates[i] + '\n\n' + events[i]
    return event

def main():
    # https://api.telegram.org/bot<token>/METHOD_NAME

    offset = 0

    while True:
        params = {
            'offset': offset,
            'timeout': 30,
        }
        api_url = 'https://api.telegram.org/bot' + TOKEN + '/getUpdates'
        data = requests.get(api_url, data=params).json()
        print('data', data)

        if not data['ok']:
            continue

        updates = data['result']

        for update in updates:
            offset = max(offset, update['update_id'] + 1)
            print(update['update_id'], update['message']['text'])

            message = update['message']
            text = message['text']
            chat_id = message['chat']['id']

            breakfast_selector = '#txt > table > tbody > tr > td:nth-child(1)'
            lunch_selector =     '#txt > table > tbody > tr > td:nth-child(2)'
            dinner_selector = '#txt > table > tbody > tr > td:nth-child(3)'

            if text == '/breakfast':
                answer = 'BREAKFAST\n\n' + get_menu(breakfast_selector)
            elif text == '/lunch':
                answer = 'LUNCH\n\n' + get_menu(lunch_selector)
            elif text == '/dinner':
                # dinner_selector = '#txt > table > tbody > tr > td.t_end'
                answer = 'DINNER\n\n' + get_menu(dinner_selector)
            elif text == '/tomorrow':
                tmr = date.today() + timedelta(days=1)
                tmr_str = tmr.isoformat()
                breakfast = get_menu(breakfast_selector, tmr_str)
                lunch = get_menu(lunch_selector, tmr_str)
                dinner = get_menu(dinner_selector, tmr_str)
                answer = ( '### TOMORROW ###\n\n'
                           'BREAKFAST\n-----------\n' + breakfast + '\n\n'
                           'LUNCH\n-----------\n' + lunch + '\n\n'
                           'DINNER\n-----------\n' + dinner + '\n\n' )
            elif text == 'im sad':
                j = json.loads(get_photo())
                image = j['message']
                answer = image
            elif text == 'bus':
                current_time = str(datetime.now().time()).split(':')
                checker = get_time()
                if datetime.now().weekday() == 6 or datetime.now().weekday() == 5:
                    answer = ('Today is weekend, no bus on campus.')
                else:
                    for i in range(len(checker)):
                        if int(current_time[0]) <= int(checker[i][0]+checker[i][1]):
                            if int(current_time[1]) <= int(checker[i][3]+checker[i][4]):
                                answer = ('Next bus will arrive at ' + str(checker[i]) + '.')
                                break
                            else:
                                continue
            elif text == 'scholarship':
                    if int(datetime.now().day) == 25:
                        answer = 'Yay, today is scholarship day!'
                    else:
                        delta = int(datetime.now().day) - 25
                        if delta > 0:
                            answer = ('You already received scholarship ' + str(delta) + ' days ago. Maybe you should count expenses?')
                        else:
                            answer = ('My condolesces, you need to wait ' + str(abs(delta)) + ' days till next scholarship. Good luck.')
            elif text == 'events':
                answer = get_events()
            else:
                answer = ( 'I dont get it 😔\n'
                           'You can use following commands:\n'
                           'To get KAIMARU menu:\n'
                           '- breakfast\n'
                           '- lunch\n'
                           '- dinner\n'
                           'To get next shuttle bus time:\n'
                           '- bus\n'
                           'To calculate days left to scholarship:\n'
                           '- scholarship\n'
                           'To see this month KAIST calendar:\n'
                           '- events\n'
                           'To cheer up 🤗:\n'
                           '- im sad\n')

            api_url = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
            params = {
                'chat_id': chat_id,
                'text': answer,
            }
            requests.post(api_url, data=params).json()

main()

bot.polling(none_stop=True)
