import os, tempfile
from django.http import HttpResponse, HttpResponseForbidden

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,
                            ImageMessage, )

from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

from .models import PhotoUrl

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


# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text='reply_message')
#     )


@handler.add(MessageEvent, message=[ImageMessage, TextMessage])
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='invalid message')
        )
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(prefix=ext + '-', delete=True) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)

        upload_result = upload(tf.name, type="private")

        if "error" in upload_result:
            error_text = 'invalid image'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=error_text)
            )
            return

        url, options = cloudinary_url(upload_result['public_id'], format=ext,
                                      crop='fill', width=100, height=100)

        PhotoUrl.objects.create(url=url)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='save image')
        )
