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
import asyncio
import traceback

import bgm

import EnvironmentVariable



# 上記で取得したアプリのトークンを入力



# テストサーバー用のトークン
BOT_TOKEN = EnvironmentVariable.get_discord_bot_token()



# パッケージのインポートとインスタンス作成
client = discord.Client()

# 他のモジュールへの伝搬が面倒なので、Pythonの組み込み変数同様の扱いにしてしまう
builtins.client = client

# 対象となるサーバーオブジェクトの取得
def get_target_server_obj(target_server_id):
    try:
        for svr in client.servers:
            if target_server_id == svr.id:
                return svr
    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        print("例外:get_target_server_obj error")


# 音の再生や停止命令を一時的に記憶する場所
# on_readyから命令を発行する場合は、強引にon_ready内で処理するよりも
# メッセージを投げた方が早い
def get_bgm_cache_channel(server):
    for ch in server.channels:
        if str(ch) == "音《一時記憶》":
            return ch
            
    return None

# 再生を意味するコマンド。まぁもう決め打ちでいいでしょ…
def get_bonshou_play_cmd():
    return "!bonshou_bgm_play bonshou_01_64k.mp3"

# フェイドアウト。 別途 stopも作ってもいいかもしれない。
def get_bonshou_fadeout_cmd():
    return "!bonshou_bgm_fadeout"

# ログイン&準備が完了したら一度だけ実行される
@client.event
async def on_ready():
    # コンソールにBOTとしてログインした名前とUSER-IDを出力
    print('Logged in as')
    print('BOT-NAME :', client.user.name)
    print('BOT-ID   :', client.user.id)
    print('------')
    
    # 起動時の時間をひかえる
    datetime_now = datetime.datetime.now()
    # 前回の時間として控える
    pre_datetime_hour = datetime_now.hour
    # 今の日付
    datetime_day = datetime_now.day

    # GOSHUIN PROJECTの一般サーバー
    goshuin_project_server = get_target_server_obj('483298368760840194')
    
    # 
    cannel_bgm_cache_channel = get_bgm_cache_channel(goshuin_project_server)

    if goshuin_project_server:

        print("サーバー発見")
        while(True):
            now_datetime = datetime.datetime.now()
            
            # 前回と同じ「時」であれば、次の「時」を待つ
            if pre_datetime_hour == now_datetime.hour:
                await asyncio.sleep(2)
                continue

            # ２段構えぐらいで、梵鐘を鳴らず、コマンドを発行
            try:
                print(cannel_bgm_cache_channel.name)
                message_obj = await client.send_message(cannel_bgm_cache_channel, get_bonshou_play_cmd() )
            except:
                await asyncio.sleep(5)
                try:
                    message_obj = await client.send_message(cannel_bgm_cache_channel, get_bonshou_play_cmd() )
                except:
                    pass

            try:
                # 発行したコマンドがどんどんたまると邪魔なので消す
                await asyncio.sleep(5)
                await client.delete_message(message_obj)
            except:
                pass                

            # コマンド発行をしたので、前回実行時間として保存を上書き。次回のために備える
            pre_datetime_hour = now_datetime.hour
            # 
            await asyncio.sleep(30)



# メッセージを受信するごとに実行される
@client.event
async def on_message(message):

    # メッセージが一致していて
    if "!bonshou_bgm" in message.content:
        # メッセージコマンド用のチャンネルと一致しているならば…
        if message.channel == get_bgm_cache_channel(message.channel.server):
            await bgm.bonshou_bgm(message)

# APP(BOT)を実行
client.run(BOT_TOKEN)
