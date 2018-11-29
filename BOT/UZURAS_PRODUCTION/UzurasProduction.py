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

# 現在の季節のディレクトリ
def GetCurrentSeasonDirectory():
    dir = "./base/winter"
    return dir

# ベースとなるイメージの取得
def GetBaseImageRelativePath(dir):
    base_list = os.listdir(dir)
    file_name = random.choice(base_list)
    base_file_path = dir + "/" + file_name
    base_image = Image.open(base_file_path)
    return base_image, file_name

# コインのロゴイメージへの相対パス
def GetCoinImageRelativePath(coinname):
    coin_logo_path = "./icon/" + coinname.upper() + ".png"
    return coin_logo_path

# 現在の時間をIntでもらう
def GetIntOfNowTimeStamp():
    # 現在のunixタイムを出す
    now = datetime.datetime.now()
    unix = now.timestamp()
    unix = int(unix)
    return unix


def make_rain_img(message, coinname, tip, user_num):
    dir = GetCurrentSeasonDirectory()
    # ベースとなるイメージと、イメージのファイル名
    base_image, file_name = GetBaseImageRelativePath(dir)
    coin_image_path = GetCoinImageRelativePath(coinname)
    if os.path.exists(coin_image_path):
        for num in range(0, 10):
            if num > user_num:
                break
            RideCoinImage(coin_image_path, base_image)
    else:
        print("ない")
        return None, None, None

    # 現在のunixタイムを出す
    unix = GetIntOfNowTimeStamp()
    
    upload_file_relative_path = str(unix) + "_" + str(message.id) + "_rain" + ".png"
    temp_file_relative_path = "RainTempImage/" + upload_file_relative_path
    
    base_image.save(temp_file_relative_path)
    return temp_file_relative_path, upload_file_relative_path, file_name

# ベースとなるイメージに１つコインを載せる
def RideCoinImage(coin_logo_path, base_image):
    # コインのイメージ
    coin_img = Image.open(coin_logo_path)
    # 大きさを適当にランダムで変更
    rand_thumb = random.randint(10, 32)
    coin_img.thumbnail( (rand_thumb, rand_thumb) )
    # 回転を適当にランダムで変更
    rand_rot = random.randint(1, 360)
    coin_img.rotate(rand_rot)
    # アルファチャンネルを考慮して
    mask = coin_img.split()[3]
    # ベースとなるイメージの上にコインイメージを乗せる
    base_image.paste(coin_img, (random.randint(0, base_image.width) ,random.randint(0, base_image.height)), mask)



# 前回削除をこころみたUnixTime
pre_datetime_unix_time = 0

# 古いファイルの削除を試みる
def TryDeleteOldImageFile(message):

    global pre_datetime_unix_time

    # 現在のunixタイムを出す
    unix = GetIntOfNowTimeStamp()

    # 前回の削除から10分以上経過していること
    if unix-pre_datetime_unix_time > 10 * 60:

        # 前回削除をこころみたUnixTime として保存
        pre_datetime_unix_time = unix

        # 1000個以上のファイルがたまっていること
        temp_dir = 'RainTempImage'
        unix = DeleteOldImageFile(temp_dir, unix)

    else:
        pass
        # print(unix-pre_datetime_unix_time)

# 古いファイルの削除
def DeleteOldImageFile(temp_dir, unix):
    files = os.listdir(temp_dir)
    if len(files) > 1000:
        for file in files:
            try:
                # ファイルはファイル名そのものが生成タイムスタンプとなっている。
                m = re.search("^[0-9]+", file)
                date = m.group(0)
                date = int(date)

                # 現在のunixタイムを出す
                unix = GetIntOfNowTimeStamp()

                # ファイルは一時ディレクトリに生成されて10分以上経過している。
                if unix-date > 600:
                    os.remove(temp_dir + '/' + file)

            except:
                print(sys.exc_info())
    return unix

# チャンネルのメッセージの削除を試みる
async def DeleteChannelAllMessage(message):
    try:
        tmp = await client.send_message(message.channel, 'チャンネルのメッセージを削除しています')
        async for msg in client.logs_from(message.channel):
            await client.delete_message(msg)
    except:
        print("削除中にエラーが発生しました")

def PrintMessageAuthorAvatorUrl(message):
    avator_url = message.author.avatar_url or message.author.default_avatar_url
    avator_url = avator_url.replace(".webp?", ".png?")
    print(avator_url)

# メッセージを受信するごとに実行される
@client.event
async def on_message(message):

    # メッセージ投稿者のアバターのURLをプリント
    # PrintMessageAuthorAvatorUrl(message)

    # BOTとメッセージの送り主が同じ人なら処理しない
    if client.user == message.author:
        return

    
    # こみやんま#0314
    if message.author.id == "397238348877529099":
        # そのチャンネルに存在するメッセージを全て削除する
        if message.content.startswith('!-!-!clear'):
            DeleteChannelAllMessage(message)
            return

    try:
        # 送信主がBOTなら処理しない
        roles = message.author.roles;
        is_uzura = False
        for r in roles:
            if r.name == "うずら":
                is_uzura = True
                
        if not is_uzura:
            return

        mrain = re.search("\<\@(.+?)\> \-\-\- ([0-9\.]+)(.+?)\(Proportional to speech amount\) \-\-\-\> (\d+) Users ", message.content, re.IGNORECASE)
        mtip = None
        if mrain:
            print(mrain.group(1)) # WHO
            print(mrain.group(2)) # AMOUNT
            print(mrain.group(3)) # COIN
            path, path2, name = make_rain_img(message, mrain.group(3), mrain.group(2), int(mrain.group(4)))
            if path and path2:
                content_message = name
                send_message_obj = await client.send_file(message.channel, path, content=content_message, filename=path2)

        else:
            mtip = re.search("\<\@(.+?)\> \-\- ([0-9\.]+)(.+?) \-\-\> (\d+) Users", message.content, re.IGNORECASE)
            if mtip:
                print("mtip")
                print(mtip.group(1)) # WHO
                print(mtip.group(2)) # AMOUNT
                print(mtip.group(3)) # COIN
                path, path2, name = make_rain_img(message, mtip.group(3), mtip.group(2), int(mtip.group(4)))
                if path and path2:
                    content_message = name
                    send_message_obj = await client.send_file(message.channel, path, content=content_message, filename=path2)

        if mrain or mtip:
            try:
                TryDeleteOldImageFile(message)
            except:
                pass



    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        print("例外:on_message error")







# APP(BOT)を実行
client.run(BOT_TOKEN)
