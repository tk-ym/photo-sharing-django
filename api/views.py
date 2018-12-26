import os, tempfile
from django.http import HttpResponse, HttpResponseForbidden

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

CHANNEL_ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
LINE_ACCESS_SECRET = os.environ["CHANNEL_SECRET"]

line_bot_api = LineBotApi(channel_access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(channel_secret=LINE_ACCESS_SECRET)


def index(request):
    return HttpResponse("This is photo sharing api.")


def callback(request):
    signature = request.META['HTTP_X_LINE_SIGNATURE']
    body = request.body.decode('utf-8')

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        HttpResponseForbidden()

    return HttpResponse('OK', status=200)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='reply_message')
    )