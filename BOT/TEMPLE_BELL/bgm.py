#coding: utf-8
# ver 2.1
# 文字の認識をよくするため

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
import difflib

import copy
import asyncio


def get_bgm_channel(server):
    for ch in server.channels:
        if str(ch) == "🔔梵鐘の音":
            return ch
            
    return None


GLOBAL_PLAYER = {}


async def start_bgm(message, bgm_path):

    channel = message.channel
    server = message.channel.server
    try:
        voice_client = client.voice_client_in(server)
        await voice_client.disconnect()
    except:
        print("ボイスチャンネルへの接続切断中にエラー")

    channel = get_bgm_channel(message.channel.server)

    voice = None
    voice_client = None
    try:
        voice = await client.join_voice_channel(channel)
        voice_client = client.voice_client_in(server)
    except Exception as e3:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e3.__traceback__))
        print("例外:start_bgm error")

    try:
        player = voice.create_ffmpeg_player(bgm_path)
        GLOBAL_PLAYER[message.author.id] = player
        asyncio.sleep(3)
        player.start()
    except Exception as e4:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e4.__traceback__))
        print("例外:start_bgm error")
    

async def fadeout_bgm(message):
    
    player = GLOBAL_PLAYER[message.author.id]

    await asyncio.sleep(0.2)
    current_volume = player.volume
    await asyncio.sleep(0.2)
    player.volume = current_volume * 0.9
    await asyncio.sleep(0.2)
    player.volume = current_volume * 0.8
    await asyncio.sleep(0.2)
    player.volume = current_volume * 0.7
    await asyncio.sleep(0.2)
    player.volume = current_volume * 0.6
    await asyncio.sleep(0.2)
    player.volume = current_volume * 0.5
    await asyncio.sleep(0.2)
    player.volume = current_volume * 0.4
    await asyncio.sleep(0.2)
    player.volume = current_volume * 0.3
    await asyncio.sleep(0.2)
    player.volume = current_volume * 0.2
    await asyncio.sleep(0.2)
    player.volume = current_volume * 0.1
    await asyncio.sleep(0.2)
    player.stop()
    current_volume = player.volume

async def stop_bgm(message):
    
    player = GLOBAL_PLAYER[message.author.id]
    player.stop()



async def bonshou_bgm(message):
    try:
        m1 = re.search("^!bonshou_bgm_play (.+)$", message.content)
        if m1:
            bgm_file = m1.group(1)
            await start_bgm(message, "bgm/" + bgm_file)
            
        m2 = re.search("^!bonshou_bgm_fadeout$", message.content)
        if m2:
            await fadeout_bgm(message)

        m3 = re.search("^!bonshou_bgm_stop$", message.content)
        if m3:
            await stop_bgm(message)

    except Exception as e5:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e5.__traceback__))
        print("例外:bonshou_bgm error")
        
