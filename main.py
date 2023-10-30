import asyncio
import json
from multiprocessing import Pool
import multiprocessing
import time
import requests

def login(username, password):
    url = 'https://better-admin.org.uk/api/auth/customer/login'
    body = {
        'username': username,
        'password': password
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Origin': 'https://myaccount.better.org.uk'
    }
    
    r = requests.post(url, json = body, headers = headers)
    data = r.json()
    # print(data)
    print('login status: ' + data['status'])
    return data

def get_courts_by_slot(token, date, start_time, end_time):
    SLEEP_INTERVAL = 1
    while True:
        url = 'https://better-admin.org.uk/api/activities/venue/queensbridge-sports-community-centre/activity/badminton-40min/slots?date=' + date + '&start_time=' + start_time + '&end_time= ' + end_time
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Origin': 'https://myaccount.better.org.uk',
            'Authorization': 'Bearer ' + token
        }
        r = requests.get(url, headers = headers)
        data = r.json()
        if r.status_code == 422:
            print('the slots are not available for now, sleep ' + str(SLEEP_INTERVAL) + 'ms')
            time.sleep(SLEEP_INTERVAL)
            continue
        return data

def select(items, keyword):
    for item in items:
        if keyword in item['location']['name']:
            return item['id']

def add(token, id):
    url = 'https://better-admin.org.uk/api/activities/cart/add'
    body = {
        'items': [
            {
                'id': id,
                'type': 'activity'
            }
        ]
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Origin': 'https://myaccount.better.org.uk',
        'Authorization': 'Bearer ' + token
    }
    
    r = requests.post(url, json = body, headers = headers)
    data = r.json()
    if r.status_code != 200:
        print('failed to add item: ', data)
        return False
    else:
        print('add item successfully')
        return True

def add_court(token, date, start, end, keyword):
    title = date + ' ' + start + '-' + end + ' ' + keyword
    print('task: ' + title)

    courts = get_courts_by_slot(token, date, start, end)
    id = select(courts['data'], keyword)
    ok = add(token, id)
    if ok == True:
        print('add to basket successfully: ' + title)
        return "SCCUESS"
    else:
        return "FAILURE"

def multi_run_wrapper(args):
   return add_court(*args)

if __name__ == '__main__':
    manager = multiprocessing.Manager()

    print('start to snap up the slots')

    user = login('BET3448609','Happyshare4us!')
    token = user['token']
    # print('token: ' + token)

    with Pool(3) as pool:
        results = pool.map(multi_run_wrapper,[
                (token, '2023-11-06', '10:20', '11:00', 'Court 4'),
                (token, '2023-11-06', '11:00', '11:40', 'Court 4'),
                (token, '2023-11-06', '11:40', '12:20', 'Court 4')
            ]
        )
    print(results)
