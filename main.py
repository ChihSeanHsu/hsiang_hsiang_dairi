from __future__ import unicode_literals

import asyncio
import configparser
from datetime import datetime, timedelta
from google import google
import multiprocessing
import os
import pytz
import random
import wikipedia

from apscheduler.schedulers.background import BackgroundScheduler
from concurrent.futures.process import ProcessPoolExecutor
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, VideoMessage, VideoSendMessage, ImageSendMessage


app = Flask(__name__)

wikipedia.set_lang("zh-tw")

config = configparser.ConfigParser()
config.read('/root/hsiang/config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

hsiang = config.get('line-bot', 'hsiang')
baobao = config.get('line-bot', 'baobao')

who = baobao

who_am_i = "翔翔老師"
what = "什麼是"
why = "為什麼"
how_to = text = f'你可以問我一些問題喔，但我只看得懂一點東西。問問題的方式是這樣\n1.{who_am_i}{why}XXXX\n2.{who_am_i}{what}XXX\n然後還有一些隱藏功能就不講惹。'
tz = pytz.timezone('Asia/Taipei')
time_without_signal = tz.localize(dt=datetime(2020, 10, 1, 7, 0, 0))
time_not_go_home = tz.localize(dt=datetime(2020, 9, 30, 18, 0, 0))
time_to_start_climbing = tz.localize(dt=datetime(2020, 10, 1, 7, 0, 0))


error_usage = 0

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        print(body, signature)
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def how_to_ask(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=how_to)
    )

@handler.add(MessageEvent, message=TextMessage)
def reply(event):
    global error_usage
    req = event.message.text
    return_text = "辛苦尼惹"
    
    if "煩" in req:
        return_text = "沒事的沒事的"
    elif "酷" in req:
        return_text = "酷"
    elif "愛" in req:
        return_text = "愛尼喔"
    elif "晚安" in req:
        return_text = "愛尼喔 晚安安喔"
    elif "午安" in req:
        return_text = "愛尼喔 午安安喔"
    elif "早安" in req:
        return_text = "愛尼喔 早安安喔"
    elif "睡覺" in req:
        return_text = "愛尼喔 晚安安喔 最愛尼了啦"
    elif "怎麼用" in req:
        return_text = how_to
    elif who_am_i in req:
        if what in req:
            ques = req.split(what)[1].strip()
            ans = wikipedia.summary(ques, sentences=1)
            return_text = ans
        elif "為什麼" in req:
            ques = req.split(who_am_i)[1].strip()
            anss = google.search(ques, 1)
            collector = []
            for idx in range(len(anss)):
                if idx > 10:
                    break
                collector.append(f'{anss[idx].name}: {anss[idx].link}\n')

            return_text = ''.join(collector)
        else:
            error_usage = 999
        if not return_text:
            return_text = '我不知道耶，我要想一下，你等等再問我。'

    else:
        error_usage += 1

    if error_usage > 3:
        how_to_ask(event)
        error_usage = 0
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=return_text)
        )
    
    
def greeting(value):
    if datetime.now(tz) >= time_without_signal:
        text = "愛尼喔 "
        for _ in range(2):
            line_bot_api.push_message(
                who,
                TextSendMessage(text=text + value)
            )
    else:
        print('not yet')

def duffy_iterator():
    video = [
        # share dropbox link and use modify query string from dl=0 to raw=1 to directly get video
        'https://www.dropbox.com/s/x2ck2v9lhpmib27/duffy_1_re.mp4?raw=1',
        'https://www.dropbox.com/s/3ez319eg8gikvux/duffy2.mp4?raw=1',
        'https://www.dropbox.com/s/xksiyb933mtpp3a/duffy3.mp4?raw=1',
        'https://www.dropbox.com/s/xhg0zs9ixbp6acu/duffy1.mp4?raw=1',
    ]
    thumbnail = [
        'https://i.imgur.com/lkkiEub.jpg',
        'https://i.imgur.com/liyGLUx.jpg',
        'https://i.imgur.com/01Q5eDf.jpg',
        'https://i.imgur.com/UAVAIsZ.jpg',
    ]
    while True:
        for i in range(len(video)):
            yield (video[i], thumbnail[i])

duffy_generator = duffy_iterator()

def post_duffy():
    if datetime.now(tz) >= time_not_go_home:
        video, thumbnail = next(duffy_generator)

        line_bot_api.push_message(
            who,
            VideoSendMessage(
                original_content_url=video,
                preview_image_url=thumbnail
            )
        )
    else:
        print('not yet')

def selfie_iterator():
    selfies = [
        'https://i.imgur.com/MwWeYly.jpg',
        'https://i.imgur.com/hIXXADA.jpg',
        'https://i.imgur.com/KmJML7r.jpg',
        'https://i.imgur.com/msRzIqc.jpg',
        'https://i.imgur.com/WZdUYcn.jpg',
        'https://i.imgur.com/sihDN0b.jpg',
        'https://i.imgur.com/xpjS5lX.jpg',
        'https://i.imgur.com/DAetlc4.jpg',
        'https://i.imgur.com/jpBRPMp.jpg',
        'https://i.imgur.com/rvkioDj.jpg',
        'https://i.imgur.com/zHyk9il.jpg', 
    ]
    while True:
        for i in range(len(selfies)):
            yield selfies[i]

selfie_generator = selfie_iterator()

def post_selfie():
    if datetime.now(tz) >= time_to_start_climbing:
        selfie = next(selfie_generator)
        line_bot_api.push_message(
            who,
            ImageSendMessage(
                original_content_url=selfie,
                preview_image_url=selfie,
            )            
        )

def test_iter():
    i = 1
    while True:
        yield i
        i += 1

test_gen = test_iter()

def test_cron():
    line_bot_api.push_message(
       hsiang,
       TextSendMessage(text=next(test_gen))
    )

test_duffy_gen = duffy_iterator()

test_time_without_signal = tz.localize(dt=datetime(2020, 8, 27, 16, 0, 0))

def test_duffy():
    if datetime.now(tz) >= test_time_without_signal:
        video, thumbnail = next(test_duffy_gen)

        line_bot_api.push_message(
            hsiang,
            VideoSendMessage(
                original_content_url=video,
                preview_image_url=thumbnail
            )
        )

def reborn(to_who):
    line_bot_api.push_message(
        to_who,
        TextSendMessage(text='我復活啦!!')
    )

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(greeting, 'cron', hour=7, minute=0, misfire_grace_time=3600, args=['早安安喔'], timezone=tz)
    scheduler.add_job(greeting, 'cron', hour=12, minute=0, misfire_grace_time=3600, args=['午安安喔'], timezone=tz)
    scheduler.add_job(greeting, 'cron', hour=0, minute=0, misfire_grace_time=3600, args=['晚安安喔'], timezone=tz)
    scheduler.add_job(post_duffy, 'cron', hour=23, minute=0, misfire_grace_time=3600, timezone=tz)
    scheduler.add_job(post_selfie, 'cron', hour=9, minute=0, misfire_grace_time=3600, timezone=tz)
    scheduler.add_job(post_selfie, 'cron', hour=15, minute=0, misfire_grace_time=3600, timezone=tz)
    scheduler.add_job(post_selfie, 'cron', hour=21, minute=0, misfire_grace_time=3600, timezone=tz)
    scheduler.start()
    
    se_g = selfie_iterator()
    selfie = next(se_g) 
    line_bot_api.push_message(
        hsiang,
        ImageSendMessage(
            original_content_url=selfie,
            preview_image_url=selfie,
        )            
    )


    d_g = duffy_iterator()

    video, thumbnail = next(d_g)

    line_bot_api.push_message(
        hsiang,
        VideoSendMessage(
            original_content_url=video,
            preview_image_url=thumbnail
        )
    )

    scheduler.print_jobs()
    import logging
    logging.basicConfig(filename='/root/debug.log',level=logging.INFO)
    reborn(hsiang)
    reborn(who)
    try:
        app.run(port=80)

    except (KeyboardInterrupt, Exception):
        scheduler.shutdown()

