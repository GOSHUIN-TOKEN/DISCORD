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

import EnvironmentVariable
import WalletAddressDeleter
import JapaneseOmikuji
import MicMessage
import NaturalChat

import RegistEtherMemberInfo
import EastAsianWidthCounter
import ImageCategory
import AirdropMemberInfo
import copy
import asyncio

import ChatLevelUp
import InviteCounter

import threading
from typing import List, NamedTuple

# 上記で取得したアプリのトークンを入力



# テストサーバー用のトークン
BOT_TOKEN = EnvironmentVariable.get_discord_bot_token()



# パッケージのインポートとインスタンス作成
client = discord.Client()

# 他のモジュールへの伝搬が面倒なので、Pythonの組み込み変数同様の扱いにしてしまう
builtins.client = client

ChatLevelUp.createChatLevelUpTable()


# ログイン&準備が完了したら一度だけ実行される
@client.event
async def on_ready():
    # コンソールにBOTとしてログインした名前とUSER-IDを出力
    print('Logged in as')
    print('BOT-NAME :', client.user.name)
    print('BOT-ID   :', client.user.id)
    print('------')


sm1, sm2, sm3, sm4, sm5 = NaturalChat.CreateObject()
print(sm1)
print(sm3)
print(sm3)
print(sm4)
print(sm5)

builtins.sm4 = sm4
builtins.sm5 = sm5

async def my_background_task_send_typing():
    pass
    
    """
    global NEED_TYPING_CHANNEL_OBJ

    await client.wait_until_ready()

    while not client.is_closed:
        await asyncio.sleep(1)
        
        if NEED_TYPING_CHANNEL_OBJ:
            await asyncio.sleep(2)
            await client.send_typing(NEED_TYPING_CHANNEL_OBJ)
            NEED_TYPING_CHANNEL_OBJ = None
    """

async def my_background_task_cache_usr_info():

    await client.wait_until_ready()

    _counter = 0
    for svr in client.servers:

        for mem in list(svr.members):
            if client.is_closed:
                break

            try:
                _usrobj = await client.get_user_info(mem.id)
                InviteCounter.USER_ID_LIST[mem.id] = _usrobj
                _counter = _counter + 1
                if _counter % 100 == 0:
                    print("User Objectを" + str(_counter) + "名キャッシュしました")

            except Exception as e:
                t, v, tb = sys.exc_info()
                print(traceback.format_exception(t,v,tb))
                print(traceback.format_tb(e.__traceback__))

    print("my_background_task_cache_usr_info 完了")


# チャンネルのメッセージの削除を試みる
async def DeleteChannelAllMessage(message):
    try:
        tmp = await client.send_message(message.channel, 'チャンネルのメッセージを削除しています')
        async for msg in client.logs_from(message.channel):
            await client.delete_message(msg)
    except:
        print("削除中にエラーが発生しました")


# メッセージを受信するごとに実行される
@client.event
async def on_message(message: discord.Message):

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
        for r in roles:
            if r.name == "BOT":
                return
            if r.name == "UZURAS･ACT":
                return
            if r.name == "TempleBell":
                return
            if r.name == "Shui":
                return
            if r.name == "巫女":
                return
            if r.name == "鐘":
                return
            if r.name == "うずら":
                return
    except:
        pass

    # こみやんま#0314
    if message.author.id == "397238348877529099":
        # そのチャンネルに存在するメッセージを全て削除する
        if message.content.startswith('!-!-!clear'):
            await DeleteChannelAllMessage(message)
            return


    # 許可されないWalletアドレスのメッセージ
    is_delete = await WalletAddressDeleter.violation_wallet_address_message(message)
    if is_delete:
        return

    # メンバー情報の表示
    if RegistEtherMemberInfo.is_show_another_member_data_condition(message):
        await RegistEtherMemberInfo.show_another_member_data(message)
        return

    # メンバー情報の表示
    if RegistEtherMemberInfo.is_show_another_ticket_data_condition(message):
        await RegistEtherMemberInfo.show_another_ticket_data(message)
        return

    # メンバー情報の表示
    if RegistEtherMemberInfo.is_show_one_member_data_condition(message):
        await RegistEtherMemberInfo.show_one_member_data(message, message.author.id)
        return

    # チケット情報表示
    if RegistEtherMemberInfo.is_show_one_ticket_data_condition(message):
        await RegistEtherMemberInfo.show_one_ticket_data(message, message.author.id)
        return

    # イーサアドレスの登録
    if RegistEtherMemberInfo.is_regist_one_member_data_condition(message):
        await RegistEtherMemberInfo.regist_one_member_data(message, message.author.id)
        return

    # メンバー情報の表示
    if AirdropMemberInfo.is_show_one_member_data_condition(message):
        await AirdropMemberInfo.show_one_member_data(message, message.author.id)
        return


    # エアドロのイーサアドレスの登録
    if AirdropMemberInfo.is_regist_one_member_data_condition(message):
        await AirdropMemberInfo.regist_one_member_data(message, message.author.id)
        return

    # ディアたんのマイクの処理
    if MicMessage.is_mic_permission_condition(message):
        await MicMessage.say_message(message)
        return

    # おみくじの集計結果
    if JapaneseOmikuji.is_report_command_condition(message.content):
        await JapaneseOmikuji.report_command(message)
        return

    # 招待数表示コマンド
    if InviteCounter.is_another_invitesraw_show_command_condition(message.content):
        await InviteCounter.another_invitesraw_show_command(message)
        return

    # 招待数表示コマンド
    if InviteCounter.is_another_invites_show_command_condition(message.content):
        await InviteCounter.another_invites_show_command(message)
        return

    # 招待数表示コマンド
    if InviteCounter.is_invites_show_command_condition(message.content):
        await InviteCounter.invites_show_command(message, message.author)
        return

    if "歌留多" in message.channel.name:
        return

    if "音《一時記憶》" in message.channel.name or "画《一時記憶》" in message.channel.name:
        return

    try:
        if ChatLevelUp.is_level_command_condition(message.content):
            await ChatLevelUp.command_show_level_infomation(message, message.author)
            return
    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))


    # イメージカテゴリ
    """
    try:
        att = ImageCategory.is_analyze_condition(message)
        if att != None:
            await ImageCategory.analyze_image(message, att)
    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        print("例外:is_analyze_condition")
        pass
    """
    
    # 会話からおみくじを得る
    try:
        await JapaneseOmikuji.get_omikuji_from_kaiwa(message)
    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        print("例外:get_omikuji_from_kaiwa")
        pass

    # 表示
    if len(message.content)> 0 and not message.content.startswith("!") :
        for regex in NaturalChat.NaturalChattableChannelRegex():
            if re.match(regex, str(message.channel)):

                # おみくじが許される条件
                if JapaneseOmikuji.is_permission_omikuji_condition(message):
                    # 2の方を使って会話
                    deme = await JapaneseOmikuji.say_embedded_omikuji_message(message)
                    await client.send_typing(message.channel)
                    if deme == None:
                        msg = await sm2.get_naturalchat_mesasge(message)
                    else:
                        msg = await sm2.get_naturalchat_mesasge(message, deme)
                    await client.send_message(message.channel, msg)

                elif "見習い巫女" in str(message.channel):
                    await client.send_typing(message.channel)
                    msg = await sm1.get_naturalchat_mesasge(message)
                    await client.send_message(message.channel, msg)

                else:
                    pass
                    """
                    # 4の方を使って会話
                    msg = await sm4.get_naturalchat_mesasge(message)
                    await client.send_message(message.channel, msg)
                    """
                    
    try:
        await ChatLevelUp.push_kaiwa_post(message, message.content)
    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        print(sys.exc_info())
        
    if message.author.id == "397238348877529099":
        if message.content == "!all_level_roles":
            await ChatLevelUp.all_member_add_level_role(message)
            



@client.event
async def on_member_join(member):
    await InviteCounter.on_member_join(member)

@client.event
async def on_member_remove(member):
    await InviteCounter.on_member_remove(member)

client.loop.create_task(my_background_task_send_typing())
client.loop.create_task(my_background_task_cache_usr_info())


# APP(BOT)を実行
client.run(BOT_TOKEN)
