# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Akitsugu Komiyama
# under the GPL v3 License.
#

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
import aiohttp

from PIL import Image
from PIL import ImageDraw

import EnvironmentVariable

from typing import Union, List, Dict, Tuple


# 上記で取得したアプリのトークンを入力



# テストサーバー用のトークン
BOT_TOKEN: str = EnvironmentVariable.get_discord_bot_token()



# パッケージのインポートとインスタンス作成
client = discord.Client()

# 他のモジュールへの伝搬が面倒なので、Pythonの組み込み変数同様の扱いにしてしまう
builtins.client = client

class UzurasInfo:
    def __init__(self):
        self.id = '443151241816834048'
        self.member_obj = None
        self.assign()

    def assign(self) -> bool:

        # 格納済みなら何もしない
        if self.member_obj != None:
            return True

        # このBOTが所属しているサーバー全てから検索
        for svr in client.servers:
            # メンバーに
            for m in svr.members:
                if m.id == self.id: # うずら
                    self.member_obj = m
                    return True

        return False

builtins.uzuras_info = None

class UzurasActInfo:
    def __init__(self, uzuras_info: UzurasInfo):
        # 自分自身の情報ではあるが、
        # 自分自信のユーザーオブジェクト⇒メンバーオブジェクトがちょっと変換が重いので
        # ここで格納しておく。
        self.id = client.user.id
        server_obj = uzuras_info.member_obj.server
        self.member_obj = server_obj.get_member(self.id)

builtins.uzuras_act_info = None


# ログイン&準備が完了したら一度だけ実行される
@client.event
async def on_ready():

    # コンソールにBOTとしてログインした名前とUSER-IDを出力
    print('Logged in as')
    print('BOT-NAME :', client.user.name)
    print('BOT-ID   :', client.user.id)
    print('------')


# Uzurasを監視するためのバックグラウンドタスク
async def my_background_task_watching_uzuras():

    await client.wait_until_ready()

    uzuras_info = UzurasInfo()
    uzuras_act_info = UzurasActInfo(uzuras_info)

    while not client.is_closed:

        if uzuras_info.member_obj:
            if uzuras_info.member_obj.status == discord.Status.online:
                await client.change_nickname(uzuras_act_info.member_obj, "うずらっぷ《起》")
            else:
                await client.change_nickname(uzuras_act_info.member_obj, "うずらっぷ《眠》")

        await asyncio.sleep(5)

# Uzurasを監視するためのバックグラウンドタスク
async def my_avator_copy_from_uzuras():

    await client.wait_until_ready()

    uzuras_info = UzurasInfo()

    while not client.is_closed:

        if uzuras_info.member_obj:
            uzuras_author = uzuras_info.member_obj
            avator_url: str = uzuras_author.avatar_url or uzuras_author.default_avatar_url
            avator_url: str = avator_url.replace(".webp?", ".png?")
            await setavatar(avator_url)

        await asyncio.sleep(60*60)

# 現在の季節のディレクトリ
def GetCurrentSeasonDirectory() -> str:

    date = datetime.datetime.now()
    year_first = datetime.datetime(date.year, 1, 1)
    diff: datetime.timedelta = date - year_first
    days = diff.days
    month_season_limit = [
        75+92*0, # 冬
        75+92*1, # 春
        75+92*2, # 夏
        75+92*3, # 秋
        75+92*4  # 冬
    ]
    if days < month_season_limit[0]:
        cur_season_dir = "winter"
    elif days < month_season_limit[1]:
        cur_season_dir = "spring"
    elif days < month_season_limit[2]:
        cur_season_dir = "summer"
    elif days < month_season_limit[3]:
        cur_season_dir = "autumn"
    elif days < month_season_limit[4]:
        cur_season_dir = "winter"

    dir = "./base/" + cur_season_dir
    return dir

# ベースとなるイメージの取得
def GetBaseImageRelativePath(dir: str):
    base_list = os.listdir(dir)
    file_name = random.choice(base_list)
    base_file_path = dir + "/" + file_name
    base_image = Image.open(base_file_path)
    return base_image, file_name

# コインのロゴイメージへの相対パス
def GetCoinImageRelativePath(coinname: str) -> str:
    coin_logo_path = "./icon/" + coinname.upper() + ".png"
    return coin_logo_path

# 現在の時間をIntでもらう
def GetIntOfNowTimeStamp() -> int:
    # 現在のunixタイムを出す
    now = datetime.datetime.now()
    unix = now.timestamp()
    unix = int(unix)
    return unix


def MakeRainImage(message: discord.Message, coinname: str, tip: int, user_num: int) -> Tuple[str, str, str]:
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
        coin_image_path = GetCoinImageRelativePath("_UNKNOWN")
        if os.path.exists(coin_image_path):
            for num in range(0, 10):
                if num > user_num:
                    break
                RideCoinImage(coin_image_path, base_image)

        print("ない")

    # 現在のunixタイムを出す
    unix = GetIntOfNowTimeStamp()

    upload_file_relative_path = str(unix) + "_" + str(message.id) + "_rain" + ".png"
    temp_file_relative_path = "RainTempImage/" + upload_file_relative_path

    base_image.save(temp_file_relative_path)
    return temp_file_relative_path, upload_file_relative_path, file_name

# ベースとなるイメージに１つコインを載せる
def RideCoinImage(coin_logo_path: str, base_image):
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
pre_datetime_unix_time: int = 0

# 古いファイルの削除を試みる
def TryDeleteOldImageFile(message: discord.Message):

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
def DeleteOldImageFile(temp_dir: str, unix: int) -> int:
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

def PrintMessageAuthorAvatorUrl(message: discord.Message) -> None:
    avator_url = message.author.avatar_url or message.author.default_avatar_url
    avator_url = avator_url.replace(".webp?", ".png?")
    print(avator_url)

# メッセージを受信するごとに実行される
@client.event
async def on_message(message: discord.Message):

    # メッセージ投稿者のアバターのURLをプリント
    # PrintMessageAuthorAvatorUrl(message)

    # BOTとメッセージの送り主が同じ人なら処理しない
    if client.user == message.author:
        return

    try:
        # 送信主がBOTなら処理しない
        roles = message.author.roles
        is_uzura = False
        for r in roles:
            if r.name == "うずら":
                is_uzura = True

        if not is_uzura:
            return

        mrain = re.search(r"\<\@(.+?)\> \-\-\- ([0-9\.]+)(.+?)\(Proportional to speech amount\) \-\-\-\> (\d+) Users ", message.content, re.IGNORECASE)
        mtip = None
        if mrain:
            print(mrain.group(1)) # WHO
            print(mrain.group(2)) # AMOUNT
            print(mrain.group(3)) # COIN
            temp_file_relative_path, upload_file_relative_path, file_name = MakeRainImage(message, mrain.group(3), mrain.group(2), int(mrain.group(4)))
            if temp_file_relative_path and upload_file_relative_path:
                content_message = file_name
                send_message_obj = await client.send_file(message.channel, temp_file_relative_path, content=content_message, filename=upload_file_relative_path)

        else:
            mtip = re.search(r"\<\@(.+?)\> \-\- ([0-9\.]+)(.+?) \-\-\> (\d+) Users", message.content, re.IGNORECASE)
            if mtip:
                print("mtip")
                print(mtip.group(1)) # WHO
                print(mtip.group(2)) # AMOUNT
                print(mtip.group(3)) # COIN
                temp_file_relative_path, upload_file_relative_path, file_name = MakeRainImage(message, mrain.group(3), mrain.group(2), int(mrain.group(4)))
                if temp_file_relative_path and upload_file_relative_path:
                    content_message = file_name
                    send_message_obj = await client.send_file(message.channel, temp_file_relative_path, content=content_message, filename=upload_file_relative_path)

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


previous_uzura_avator_url = ""
async def setavatar(uzura_avator_url: str):

    global previous_uzura_avator_url

    # 同じだったら更新しない
    if previous_uzura_avator_url == uzura_avator_url:
        return
    previous_uzura_avator_url = uzura_avator_url

    data = None
    async with aiohttp.ClientSession() as session:
        async with session.get(uzura_avator_url) as r:
            data = await r.read()

    if data == None:
        return

    await client.edit_profile(avatar=data)
    print("Avator Url is update!")


client.loop.create_task(my_background_task_watching_uzuras())
client.loop.create_task(my_avator_copy_from_uzuras())

# APP(BOT)を実行
client.run(BOT_TOKEN)
