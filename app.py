from flask import Flask, request, abort

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
    mag = event.message.text
    r = event.message.text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=r))



if __name__ == "__main__":
    app.run()

# Your Account SID from twilio.com/console
account_sid = "ACbb17bc67f6247ac1cf987d433e8e15fd"
# Your Auth Token from twilio.com/console
auth_token  = "2a30547eb0c7eb73b023d44828e9607e1"
client = Client(account_sid, auth_token)

message = client.messages.create(
    to="+886939525301", 
    from_="+18024414035",
    body="YES,今天好天氣*3")