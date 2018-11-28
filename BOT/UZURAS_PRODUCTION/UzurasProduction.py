#coding: utf-8
# ver 2.1

import builtins
import re
import random
import requests
import json
import types
import base64
import os
import sys, datetime, time
import discord
import traceback
import unicodedata

import copy
import asyncio

from PIL import Image
from PIL import ImageDraw

import EnvironmentVariable




# 上記で取得したアプリのトークンを入力



# テストサーバー用のトークン
BOT_TOKEN = EnvironmentVariable.get_discord_bot_token()



# パッケージのインポートとインスタンス作成
client = discord.Client()

# 他のモジュールへの伝搬が面倒なので、Pythonの組み込み変数同様の扱いにしてしまう
builtins.client = client


# ログイン&準備が完了したら一度だけ実行される
@client.event
async def on_ready():
    # コンソールにBOTとしてログインした名前とUSER-IDを出力
    print('Logged in as')
    print('BOT-NAME :', client.user.name)
    print('BOT-ID   :', client.user.id)
    print('------')


def make_rain_img(message, coinname, tip):
    base_list = os.listdir("./base/winter")
    base_file_path = "./base/winter/" + random.choice(base_list)
    base = Image.open(base_file_path)

    coin_logo_path = "./icon/" + coinname.upper() + ".png"
    print("coin_logo_path:" + coin_logo_path)
    if os.path.exists(coin_logo_path):
        print("ある")
        for k in range(0, 5):
            ride_coin_image(coin_logo_path, base)
    else:
        print("ない")
        return None, None

    # 現在のunixタイムを出す
    now = datetime.datetime.now()
    unix = now.timestamp()
    unix = int(unix)
    
    path2 = str(unix) + "_" + str(message.id) + "_rain" + ".png"
    path = "RainTempImage/" + path2
    print("path:"+path)
    print("path2:"+path2)
    
    base.save(path)
    ### aaa = Image.alpha_composite(black, green)
    # layers = Image.alpha_composite(black, frame)
    # layers.save("level_up_image_{0:03d}".format(i)+ ".png")
    return path, path2

def ride_coin_image(coin_logo_path, base):
    coin_img = Image.open(coin_logo_path)
    rand_thumb = random.randint(10, 32)
    coin_img.thumbnail( (rand_thumb, rand_thumb) )
    rand_rot = random.randint(1, 360)
    coin_img.rotate(rand_rot)
    mask = coin_img.split()[3]
    base.paste(coin_img, (random.randint(0, 230) ,random.randint(0, 150)), mask)


def make_tip_img(coinname, tip):
    base = Image.open("card/ZBASE.png")

    x = 0
    for c in displays_cards:
        card_img = Image.open("card/" + c + ".png")
        base.paste(card_img, (x,0))
        x = x + card_img.width

    # base.save("aaa.png")

    # 現在のunixタイムを出す
    now = datetime.datetime.now()
    unix = now.timestamp()
    unix = int(unix)
    
    path2 = str(unix) + "_" + str(message.id) + "_poker" + ".png"
    path = "DataTempImage/" + path2
    base.save(path)
    ### aaa = Image.alpha_composite(black, green)
    # layers = Image.alpha_composite(black, frame)
    # layers.save("level_up_image_{0:03d}".format(i)+ ".png")
    return path, path2


# メッセージを受信するごとに実行される
@client.event
async def on_message(message):

    try:
        print(message.channel.id)
    except:
        pass

    # BOTとメッセージの送り主が同じ人なら処理しない
    if client.user == message.author:
        return

    try:
        # 送信主がBOTなら処理しない
        roles = message.author.roles;
        is_uzura = False
        for r in roles:
            if r.name == "うずら":
                is_uzura = True
                
        #if not is_uzura:
        #    return

        mrain = re.search("\<\@(.+?)\> \-\-\- ([0-9\.]+)(.+?)\(Proportional to speech amount\) \-\-\-\>", message.content, re.IGNORECASE)
        mtip = re.search("\<\@(.+?)\> \-\- ([0-9\.]+)(.+?) \-\-\> ", message.content, re.IGNORECASE)
        print(mtip)
        if mrain:
            print(mrain.group(1)) # WHO
            print(mrain.group(2)) # AMOUNT
            print(mrain.group(3)) # COIN
            path, path2 = make_rain_img(message, mrain.group(3), mrain.group(2))
            if path and path2:
                content_message = "..."
                send_message_obj = await client.send_file(message.channel, path, content=content_message, filename=path2)

        elif mtip:
            print(mtip.group(1)) # WHO
            print(mtip.group(2)) # AMOUNT
            print(mtip.group(3)) # COIN


    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        print("例外:on_message error")







# APP(BOT)を実行
client.run(BOT_TOKEN)
