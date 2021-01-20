from flask import Flask, request, abort, jsonify , render_template#增加了 render_template
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
import random#新增1113
import json
import tempfile, os#1106
from imgurpython import ImgurClient#1106
import pandas as pd

from datetime import datetime,timezone,timedelta
from config import client_id, client_secret, album_id, access_token, refresh_token, line_channel_access_token, \
    line_channel_secret, uesr_name_myself#載入帳號設定


app = Flask(__name__, template_folder='template')#app = Flask(__name__, template_folder='template')

line_bot_api = LineBotApi(line_channel_access_token)
handler = WebhookHandler(line_channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')#在目前相對路徑上建立料夾

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
#台灣時間
def taiwan_time( hour= 8):
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    time = dt1.astimezone(timezone(timedelta(hours= hour)))
    return time


@handler.add(MessageEvent, message=(TextMessage, ImageMessage))
def handle_message(event):
    if isinstance(event.message, TextMessage):

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
        elif '@thsr' in input_text:
            now_day = taiwan_time().strftime("%Y/%m/%d")
            now_time = taiwan_time().strftime("%H:%M")
            url = 'https://www.thsrc.com.tw/TimeTable/Search'
            thsrc_station = { '南港':'NanGang', '台北':'TaiPei', '板橋':'BanQiao', '桃園':'TaoYuan', '新竹':'XinZhu', '苗栗':'MiaoLi', '台中':'TaiZhong', '彰化':'ZhangHua', '雲林':'YunLin', '嘉義':'JiaYi', '台南':'TaiNan', '左營':'ZuoYing'}
            
            ss = str(event.message.text)[5:7]
            es = str(event.message.text)[-2:]
            if ss == "":
                ss = '南港'
                es = '桃園'
            form_data = {
            'SearchType':'S',
            'Lang': 'TW',
            'StartStation': thsrc_station[ss],
            'EndStation': thsrc_station[es],
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
                '從'+ ss: departure_times,
                '到'+ es: arrival_times,
                '行車時間': duration,
                '自由坐車廂': nonreservedcar},
                columns = [ '從'+ ss, '到'+ es, '行車時間', '自由坐車廂'], index = train_numbers)
            filter = highway_df["從"+ ss] > now_time
            highway_df1 = highway_df[filter]



            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f'{highway_df1}')) 

        elif input_text == '@ID':   
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f'{user_id}'))#(text=f'{user_id}')

        elif input_text == '@mobile':
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


        elif '@tr' in input_text:
            now_day = taiwan_time().strftime("%Y/%m/%d")
            now_time = taiwan_time().strftime("%H:%M")
            url = 'https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip112/querybytime'
            taiwan_railway_station = {'基隆':'0900-基隆','三坑':'0910-三坑','八堵':'0920-八堵','七堵':'0930-七堵','百福':'0940-百福','五堵':'0950-五堵','汐止':'0960-汐止','汐科':'0970-汐科','南港':'0980-南港','松山':'0990-松山','台北':'1000-臺北','臺北-環島':'1001-臺北-環島','萬華':'1010-萬華','板橋':'1020-板橋','浮洲':'1030-浮洲','樹林':'1040-樹林', \
            '南樹林':'1050-南樹林','山佳':'1060-山佳','鶯歌':'1070-鶯歌','桃園':'1080-桃園','內壢':'1090-內壢','中壢':'1100-中壢','埔心':'1110-埔心','楊梅':'1120-楊梅','富岡':'1130-富岡','新富':'1140-新富','北湖':'1150-北湖','湖口':'1160-湖口','新豐':'1170-新豐','竹北':'1180-竹北','北新竹':'1190-北新竹','千甲':'1191-千甲','新莊':'1192-新莊','竹中':'1193-竹中', \
            '六家':'1194-六家','上員':'1201-上員','榮華':'1202-榮華','竹東':'1203-竹東','橫山':'1204-橫山','九讚頭':'1205-九讚頭','合興':'1206-合興','富貴':'1207-富貴','內灣':'1208-內灣','新竹':'1210-新竹'}

            ss = (str(z)[3:5])
            es= (str(z)[-2:])
            if ss == "":
                ss = '埔心'
                es = '台北'
            form_data = {
                'startStation': taiwan_railway_station[ss],
                'endStation': taiwan_railway_station[es],
                'transfer': 'ONE',
                'rideDate': now_day,
                'startOrEndTime': 'true',
                'startTime': '00:00',
                'endTime': '23:59',
                'trainTypeList': 'ALL',
                '_isQryEarlyBirdTrn': 'on',
                'query': '查詢'
            }

            response_post = requests.post(url, data=form_data)
            response_post.text
            soup = BeautifulSoup(response_post.text, 'html.parser')

            train_number = soup.find_all('a',{'class': ['links icon-fa icon-train chukuang','links icon-fa icon-train', \
                'links icon-fa icon-train taroko','links icon-fa icon-train tzechiang','links icon-fa icon-train puyuma']})
            d_and_a_time = soup.find_all('span', {'class': 'time'})
            durations = soup.find_all('tr', {'class': 'trip-column'})#('tr', {'class': 'train-number'})
            location = soup.find_all('span',{'class':'location'})

            # 班車資訊
            train_number_infs = []
            count = 1
            start_station = None
            end_station = None
            for locat in location:
                if (count % 6) == 1:
                    start_station = (locat.text)
                elif (count % 6) == 4:
                    end_station = (locat.text)
                elif (count % 6) == 0:
                    train_number_infs.append( '('+ start_station+ '->' + end_station+ ')')
                count +=1

            # 所有班車(train_number)合併班車資訊
            train_numbers = []
            count = 0
            for item in train_number:
                train_numbers.append(item.text+train_number_infs[count])
                count +=1

            # 所有出發時間(departure_time)
            # 所有到達時間(arrival_time)
            departure_times = []
            arrival_times = []
            count = 1
            for item in d_and_a_time:
                if (count % 2) == 0:
                    arrival_times.append(item.text)
                else:
                    departure_times.append(item.text)
                count += 1

            # 所有行車時間(duration)
            duration = []
            for i in range(len(departure_times)):
                durations_ = durations[i].find_all('td')
                duration.append(durations_[3].text)

            # 整理成表格
            import pandas as pd

            taiwan_railway_df = pd.DataFrame({
                '車次': train_numbers,
                '從'+ ss: departure_times,
                '到'+ es: arrival_times,
                '行車時間': duration},
                columns = ['從'+ ss, '到'+ es,'行車時間'], index = train_numbers )
            pd.set_option("display.max_rows", None)
            filter = taiwan_railway_df["從"+ ss] > now_time
            taiwan_railway_df = taiwan_railway_df[filter]

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= f'{ taiwan_railway_df}'))



                


    if isinstance(event.message, ImageMessage):



        user_id = event.source.user_id
        if str(user_id) in uesr_name_myself:
            user_id = uesr_name_myself[user_id]
        ext = 'jpg'
        #static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
        message_content = line_bot_api.get_message_content(event.message.id)#(event.message.id)
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name


        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)#basename() 用於去掉目錄的路徑，只返回文件名
        os.rename(tempfile_path, dist_path)#修改檔案名稱(修改前,修改後)
        try:
            client = ImgurClient(client_id, client_secret, access_token, refresh_token)
            config = {
                'album': album_id,
                'name': user_id,
                'title': user_id+' updata',
                'description': f'{taiwan_time()}'
            }
            path = os.path.join('static', 'tmp', dist_name)#合併目錄
            client.upload_from_path(path, config=config, anon=False)
            os.remove(path)
            print(path)
            print(os.path.abspath(__file__))
            if str(event.source.user_id) not in uesr_name_myself:
                user_id = '您'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= user_id+'的好圖我收了'))
        except:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='上傳失敗'))
        return 0




            

if __name__ == "__main__":
    app.run()

