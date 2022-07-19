from flask import Flask, request, jsonify
import json
import os
import requests
from lxml import html
import random

api_key = os.environ['API_KEY']
api_token = os.environ['API_TOKEN']
sms_url = os.environ['SMS_URL']
sender_id = os.environ['SENDER_ID']
recipient = os.environ['RECIPIENT']


app = Flask(__name__)

def send_sms(to,msg):
    su = sms_url + "?sendsms&apikey=" + api_key + "&apitoken=" + api_token + "&type=sms&from=" + sender_id + "&to=" + to + "&text=" + msg + "&route=0"
    r = requests.get(su)
    print("SEND_SMS",r.content)

def scrap_xe(amount, fc, tc):
    url = "https://www.xe.com/currencyconverter/convert/?Amount=" + str(amount) + "&From=" + fc + "&To=" + tc + "&xkey=" + str(random.randint(100000,999999))
    path = '//*[@id="__next"]/div[2]/div[2]/section/div[2]/div/main/form/div[2]/div[1]/p[2]'
    res = requests.get(url,headers={'Cache-Control': 'no-cache'})
    if res.status_code == 200:
        sc = html.fromstring(res.content)
        tree = sc.xpath(path)
        print(tree[0].text_content())
        ch = tree[0].text_content().split(" ")[0]
        msg = '{:,.2f}'.format(float(amount)) + " " + fc + " = " + '{:,.2f}'.format(float(ch.replace(",",""))) + " " + tc
        return msg
    else:
        return None


@app.route('/')
def hello_world():
    return '<h1>Yeah, that is Zappa! Zappa! Zap! Zap!</h1>'


@app.route('/extoday',methods=['GET', 'POST'])
def get_extoday():
    content = request.json
    print(content)
    msgs = list()
    for i in content:
        msgs.append(scrap_xe(i['amount'],i['from'],i['to']))
    ms = ",\n".join(msgs)
    send_sms(recipient,ms)
    return jsonify({"message":ms})


@app.route('/autoex',methods=['GET'])
def get_extoday_auto():
    content = [{
                    "amount": 12000,
                    "from": "EUR",
                    "to": "CAD",
                    "source": [
                    "XE",
                    "SAMPATH"
                    ]
                },
                {
                    "amount": 945,
                    "from": "USD",
                    "to": "CAD",
                    "source": [
                    "XE",
                    "SAMPATH"
                    ]
                }
            ]
    msgs = list()
    for i in content:
        msgs.append(scrap_xe(i['amount'],i['from'],i['to']))
    ms = ",\n".join(msgs)
    send_sms(recipient,ms)
    return jsonify({"message":ms})

# We only need this for local development.
if __name__ == '__main__':
    app.run()