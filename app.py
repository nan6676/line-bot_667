from flask import Flask, request, abort, jsonify
import requests

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

#from twilio.rest import Client

#import requests
from bs4 import BeautifulSoup

import json

import pandas as pd

from datetime import datetime,timezone,timedelta

app = Flask(__name__)

line_bot_api = LineBotApi('8NDvVLUVZqlsmuVRXT0BcD2Qv8CDCXfCF/JCnsw7sla2ZV/HzgdYiMxJIjNKbEChLivFSlzZVmEVzGqmERk1sMcBoIqBqrrTQ35+PkQYJcKBSXoerddVUNcseYxBVGFSq8RD6dEtGwSl23mmr/r7eQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('a5ccb4720386225cccbe5f66d1c9978d')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #mag = event.message.text
    #r = event.message.text
    #s = str(mag)[::-1]
    #r = s
    #r.split(r = "")
    #str(r)[::-1]
    #line_bot_api.reply_message(
        #event.reply_token,  
        #TextSendMessage(text=r))
    input_text = event.message.text
    if input_text == '@查詢匯率':
        resp = requests.get('https://tw.rter.info/capi.php')
        currency_data = resp.json()
        usd_to_twd = currency_data['USDTWD']['Exrate']

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'美元 USD 對台幣 TWD：1:{usd_to_twd}'))
    elif input_text == '@回家':
        dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
        dt2 = dt1.astimezone(timezone(timedelta(hours=8)))
        now_day = dt2.strftime("%Y/%m/%d")
        now_time = dt2.strftime("%H:%M")
        url = 'http://www.thsrc.com.tw/tw/TimeTable/Search'
        form_data = {
        'StartStation':'2f940836-cedc-41ef-8e28-c2336ac8fe68',
        'StartStationName': '南港站',
        'EndStation':'fbd828d8-b1da-4b06-a3bd-680cdca4d2cd',
        'EndStationName': '桃園站',
        'DepartueSearchDate': now_day,
        'DepartueSearchTime': now_time,
        'SearchType':'S'    
        }
        # 用request.post，並放入form_data
        
        response_post = requests.post(url, data=form_data)
        response_post.text

        # 用json解析, 並分析資料結構
        data = json.loads(response_post.text)
        #data


        trainItem = data['data']['DepartureTable']['TrainItem']

        # 所有班車(train_number)
        train_numbers = []
        for item in trainItem:
            train_numbers.append(item['TrainNumber'])

        # 所有出發時間(departure_time)
        departure_times = []
        for item in trainItem:
            departure_times.append(item['DepartureTime'])

        # 所有到達時間(arrival_time)
        arrival_times = []
        for item in trainItem:
            arrival_times.append(item['DestinationTime'])

        # 所有行車時間(duration)
        duration = []
        for item in trainItem:
            duration.append(item['Duration'])

        # 整理成表格
        highway_df = pd.DataFrame({
            '車次': train_numbers,
            '出發時間': departure_times,
            '到達時間': arrival_times,
            '行車時間': duration},
            columns = ['車次', '南港出發', '到達桃園', '行車時間'])

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'{highway_df}'))    




            

            


if __name__ == "__main__":
    app.run()

