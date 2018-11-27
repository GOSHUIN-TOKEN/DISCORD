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


def make_rain_img(coinname, tip):
    base = Image.open("card/ZBASE.png")

    x = 0
    for c in displays_cards:
        card_img = Image.open("base/momiji" + c + ".png")
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

        mrain = re.search("\@(.+?) \-\-\- ([0-9\.]+)(.+?)\(Proportional to speech amount\) \-\-\-\>", message.content, re.IGNORECASE)
        mtip = re.search("\@(.+?) \-\- ([0-9\.]+)(.+?) \-\-\> ", message.content, re.IGNORECASE)
        print(mtip)
        if mrain:
            print(mrain.groups(1))
            print(mrain.groups(2))
            print(mrain.groups(3))

        elif mtip:
            print(mtip.groups(1))
            print(mtip.groups(2))
            print(mtip.groups(2))


    except:
        pass







# APP(BOT)を実行
client.run(BOT_TOKEN)
