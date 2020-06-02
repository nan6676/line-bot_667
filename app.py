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

from twilio.rest import Client


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
    if input_text == '@查詢匯率':
        resp = requests.get('https://tw.rter.info/capi.php')
        currency_data = resp.json()
        usd_to_twd = currency_data['USDTWD']['Exrate']

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'美元 USD 對台幣 TWD：1:{usd_to_twd}'))


if __name__ == "__main__":
    app.run()

