from flask import Flask, request, abort, jsonify, render_template#增加了 render_template
import requests

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

from linebot.exceptions import LineBotApiError
#from twilio.rest import Client

#import requests
from bs4 import BeautifulSoup

import json
import tempfile, os#1106
from imgurpython import ImgurClient#1106
import pandas as pd

from datetime import datetime,timezone,timedelta

app = Flask(__name__, template_folder='template')

line_bot_api = LineBotApi('8NDvVLUVZqlsmuVRXT0BcD2Qv8CDCXfCF/JCnsw7sla2ZV/HzgdYiMxJIjNKbEChLivFSlzZVmEVzGqmERk1sMcBoIqBqrrTQ35+PkQYJcKBSXoerddVUNcseYxBVGFSq8RD6dEtGwSl23mmr/r7eQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('a5ccb4720386225cccbe5f66d1c9978d')

client_id ='9dbe76c69af5489'
client_secret = 'b34838057c99d05b97e433dda73976c1727cf4ae'
access_token = "3262520325f32d484f02009e34491aab4ba42507"
refresh_token = "d4a1fd24541add0b69475d718fa428e53c7c06c9"
album_id = "0bIsRbS"#p97VJXu


static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
'''try:#傳送訊息給指定的人
    line_bot_api.push_message('Uc607ab2ccc4ac029f44b743c7b1338bc', TextSendMessage(text='Hello World!'))#傳送訊息給指定的人
except LineBotApiError as e:
     error handle
    ...'''
# 增加的這段放在下面
@app.route("/")
def home():
    return render_template("home.html")

# 接收 LINE 的資訊
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

    # get user id when reply
    user_id = event.source.user_id
    #print("user_id =", user_id)
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
        url = 'https://www.thsrc.com.tw/TimeTable/Search'
        form_data = {
        'SearchType':'S',
        'Lang': 'TW',
        'StartStation': 'NanGang',
        'EndStation': 'TaoYuan',
        'OutWardSearchDate': now_day,
        'OutWardSearchTime': now_time,
        'ReturnSearchDate': now_day,
        'ReturnSearchTime': now_time    
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

        # 自由坐車廂(NonReservedCar)
        nonreservedcar = []
        for item in trainItem:
            nonreservedcar.append(item['NonReservedCar'])            

        # 整理成表格
        highway_df = pd.DataFrame({
            '車次': train_numbers,
            '從南港': departure_times,
            '到桃園': arrival_times,
            '行車時間': duration,
            '自由坐車廂': nonreservedcar},
            columns = [ '從南港', '到桃園', '行車時間', '自由坐車廂'], index = train_numbers)
        filter = highway_df["從南港"] > now_time
        highway_df1 = highway_df[filter]



        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'{highway_df1}')) 

    elif input_text == '@ID':   
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'{user_id}'))#(text=f'{user_id}')

    elif input_text == '@話題':
        web = 'https://www.mobile01.com/hottopics.php'
        res = requests.get(web, headers={'User-Agent': 'Custom'})
        soup = BeautifulSoup(res.text, 'html.parser')
        articles = soup.select('.c-listTableTd__title a')
        issue = []
        form = []
        forum = []
        line = 'Mobile01熱門討論'+'\n'
        
        for each_title in articles:
            if 'title' in (str(each_title)):
                issue.append(each_title.text)
                form.append('https://www.mobile01.com/'+ each_title['href'])
            elif 'span' in (str(each_title)):
                forum.append(each_title.text)

        count = (len(issue))
        for x in range(count):
            line = (str(line))+ ((str(x))+'.■ '+ issue[x]+' '+ forum[x]+ ' ' + form[x] +'\n')
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text= f'{ line}'))

    
    elif input_text == '@ptt':
        web = 'https://disp.cc/b/PttHot'
        res = requests.get(web)
        soup = BeautifulSoup(res.text, 'html.parser')
        articles = soup.select('.row2 a')

        issue = []
        form = []
        forum = []
        line = 'PTT熱門討論'+'\n'

        for each_title in articles:
            if 'titleColor' in (str(each_title)):
                issue.append(each_title.text)
                form.append('https://disp.cc/b/'+ each_title['href'])
            elif 'target' in (str(each_title)):
                forum.append(each_title.text)
        
        count = (len(issue))
        for x in range(count):
            line = (str(line))+ ((str(x))+'.'+ issue[x]+' '+ form[x] +'\n')

        line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text= f'{ line}'))
                


@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    if isinstance(event.message, ImageMessage):

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='好圖'))
        ext = 'jpg'
        message_content = line_bot_api.get_message_content(event.message.id)
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name


        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path, dist_path)
        try:
            client = ImgurClient(client_id, client_secret, access_token, refresh_token)
            config = {
                'album': album_id,
                'name': 'Catastrophe!',
                'title': 'Catastrophe!',
                'description': f'test-{datetime.now()}'
            }
            path = os.path.join('static', 'tmp', dist_name)
            client.upload_from_path(path, config=config, anon=False)
            os.remove(path)
            print(path)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='上傳成功'))
        except:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='上傳失敗'))
        return 0




            

if __name__ == "__main__":
    app.run()

