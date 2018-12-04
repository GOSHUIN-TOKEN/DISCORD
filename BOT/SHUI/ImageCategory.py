#coding: utf-8
# ver 2.3


import builtins
import asyncio

import re
import random
import json
import types
import require
import requests
import os
import sys, datetime, time
import glob
import discord
import traceback

import JapaneseOmikuji


        

def get_docomo_naturalchat_key():
    KEY = os.getenv("DISCORD_DOCOMO_IMAGERECOGNITION_KEY", r'')
    return {"KEY":KEY}

def get_image_type(fname):
    if fname.endswith(".png"):
        return 'image/png'
    if fname.endswith(".jpg"):
        return 'image/jpeg'
    if fname.endswith(".jpeg"):
        return 'image/jpeg'

    return 'image/png'

def get_image_ext(fname):
    if fname.endswith(".png"):
        return '.png'
    if fname.endswith(".jpg"):
        return '.jpg'
    if fname.endswith(".jpeg"):
        return '.jpg'

    return '.png'


#画像データを投げて、カテゴリの候補上位5つを取得 (カテゴリ認識)
def getImageCategory(fname, modelName="scene"):

    APIKEY = get_docomo_naturalchat_key()["KEY"]
    url = 'https://api.apigw.smt.docomo.ne.jp/imageRecognition/v1/concept/classify/'
    params = {'APIKEY': APIKEY}

    with open(fname, 'br') as f:
        data = f.read()

    files = {
        'modelName': (None, modelName, 'text/plain; charset=utf-8'),
        'image': (os.path.basename(fname), data, get_image_type(fname))
    }

    result = requests.post(
        url = url,
        params = params,
        files = files
    )
    data = result.json()
    print(data)    
    if "candidates" in data:
        json = data["candidates"]
        tag0 = json[0]["tag"]
        print(tag0)
        score0 = json[0]["score"]
        print(score0)
        
        if len(json) == 1:
            return tag0, score0, None, None, None, None

        tag1 = None
        score1 = None
        tag2 = None
        score2 = None
        if len(json) == 2:
            tag1 = json[1]["tag"]
            print(tag0)
            score1 = json[1]["score"]
            print(score0)
            return tag0, score0, tag1, score1, None, None

        if len(json) >= 3:
            tag1 = json[1]["tag"]
            print(tag0)
            score1 = json[1]["score"]
            print(score0)
            tag2 = json[2]["tag"]
            print(tag0)
            score2 = json[2]["score"]
            print(score0)
            return tag0, score0, tag1, score1, tag2, score2
        
        
    return None, None, None, None, None, None


#画像データを投げて、カテゴリの候補上位5つを取得 (カテゴリ認識)
def getImageScene(fname, modelName, message):

    APIKEY = get_docomo_naturalchat_key()["KEY"]
    url = 'https://api.apigw.smt.docomo.ne.jp/imageRecognition/v1/concept/classify/'
    params = {'APIKEY': APIKEY}

    with open(fname, 'br') as f:
        data = f.read()

    files = {
        'modelName': (None, modelName, 'text/plain; charset=utf-8'),
        'image': (os.path.basename(fname), data, get_image_type(fname))
    }
    
    result = requests.post(
        url = url,
        params = params,
        files = files
    )
    data = result.json()
    # print(data)    
    if "candidates" in data:
        json = data["candidates"]

        print(json)

        
        tag0 = json[0]["tag"]
        print(tag0)
        score0 = json[0]["score"]
        print(score0)

        if "今日のご飯" in message.channel.name:
            if "食事" in str(json):
                tag0 = "食事・料理"
                print("★食事料理に矯正")
                if score0 < 0.5:
                    score0 = 0.99
                
        # 返す値
        retData = {"MainTagName":tag0, "MainScore":score0}
        
        
        subTagName = None
        subScore = None
        subTagName1 = None
        subScore1 = None
        subTagName2 = None
        subScore2 = None
        
        if tag0 == "建物":
            subTagName, subScore, subTagName1, subScore1, subTagName2, subScore2  = getImageCategory(fname, modelName="landmark")
        if tag0 == "花":
            subTagName, subScore, subTagName1, subScore1, subTagName2, subScore2  = getImageCategory(fname, modelName="flower")
        if tag0 == "食事・料理":
            print("★★★ここだよここ")
            subTagName, subScore, subTagName1, subScore1, subTagName2, subScore2 = getImageCategory(fname, modelName="food")
        if tag0 == "寺社・仏閣・城":
            subTagName, subScore, subTagName1, subScore1, subTagName2, subScore2  = getImageCategory(fname, modelName="landmark")
        if tag0 == "風景":
            subTagName, subScore, subTagName1, subScore1, subTagName2, subScore2  = getImageCategory(fname, modelName="landmark")
        if tag0 == "夜景":
            subTagName, subScore, subTagName1, subScore1, subTagName2, subScore2  = getImageCategory(fname, modelName="landmark")
        if tag0 == "遊園地":
            subTagName, subScore, subTagName1, subScore1, subTagName2, subScore2  = getImageCategory(fname, modelName="landmark")

        # その他ですね!!などというわけにはいかないので、
        # subがその他なら、評価を消す
        if subTagName == "その他":
            subTagName = None
            subScore = None

        if subTagName:
            subTagNameArr = subTagName.split("/")
            if len(subTagNameArr) > 1:
                subTagName = subTagNameArr[1]

        retData["SubTagName"] = subTagName
        retData["SubScore"] = subScore
        retData["SubTagName1"] = subTagName1
        retData["SubScore1"] = subScore1
        retData["SubTagName2"] = subTagName2
        retData["SubScore2"] = subScore2

        return retData

    return None

def is_analyze_condition(message):
    try:
        attach_list = message.attachments
        if len(attach_list) > 0:
            att = attach_list[0]
            if "url" in att and "filename" in att and "width" in att and "height" in att:
                fn = att["filename"]
                if fn.endswith(".png") or fn.endswith(".jpg") or fn.endswith(".jpeg"):
                    return att["url"]
    except:
        print(sys.exc_info())
    
    return None



async def download(url, file_name):
    try:
        # open in binary mode
        with open(file_name, "wb") as fw:
            # get request
            res = requests.get(url)
            # write to file
            fw.write(res.content)
            print("download image:" + file_name)
            return file_name
    except:
        print(sys.exc_info())
        
    return None


async def analyze_image(message, url):
    try:
        # ビンゴは反応しない
        if "ビンゴ" in message.channel.name:
            return
            
        # 投稿が多いので間引く
        if "見ちゃイヤ" in message.channel.name:
            if random.randint(1,15) <= 14:
                return
            
        delete_old_image(message)
        
        # 現在のunixタイムを出す
        now = datetime.datetime.now()
        unix = now.timestamp()
        unix = int(unix)
        
        ext = get_image_ext(url)
        
        dwImageFilePath = await download(url, "DataTempImage/" + str(unix) + ext)
        # 保存に成功していたら
        if dwImageFilePath:
            resultAnalyzeData = getImageScene(dwImageFilePath, "scene", message)
            print(resultAnalyzeData)

            if ("今日のご飯" in message.channel.name and resultAnalyzeData["MainTagName"] == "食事・料理"):
                print("★★今日のご飯特殊処理")
                
                # メインもサブも0.8以上
                if "SubScore" in resultAnalyzeData and resultAnalyzeData["SubScore"] != None and resultAnalyzeData["SubScore"] > 0.8:
                    print("合格1")
                    await replay_image_message(message, resultAnalyzeData["SubTagName"])

                # メインもサブも0.5以上
                elif "SubScore" in resultAnalyzeData and resultAnalyzeData["SubScore"] != None and resultAnalyzeData["SubScore"] > 0.5:
                    print("合格2")
                    await replay_image_message(message, resultAnalyzeData["SubTagName"], False)

                # ２つ以上あって、0.3以上が２つ
                elif ("SubScore" in resultAnalyzeData and resultAnalyzeData["SubScore"] != None and resultAnalyzeData["SubScore"] > 0.3) and ("SubScore1" in resultAnalyzeData and resultAnalyzeData["SubScore1"] != None and resultAnalyzeData["SubScore1"] > 0.25):
                    print("合格3")
                    await replay_image_message(message, resultAnalyzeData["SubTagName"] + "と、" + resultAnalyzeData["SubTagName1"] , False)

                # ３つ以上あって、0.15以上が３つ
                elif ("SubScore" in resultAnalyzeData and resultAnalyzeData["SubScore"] != None and resultAnalyzeData["SubScore"] > 0.15) and ("SubScore1" in resultAnalyzeData and resultAnalyzeData["SubScore1"] != None and resultAnalyzeData["SubScore1"] > 0.14) and ("SubScore2" in resultAnalyzeData and resultAnalyzeData["SubScore2"] != None and resultAnalyzeData["SubScore2"] > 0.13):
                    print("合格4")
                    await replay_image_message(message, resultAnalyzeData["SubTagName"] + "と、" + resultAnalyzeData["SubTagName1"] + "、それと " + resultAnalyzeData["SubTagName2"] , False)
                    

            # まずはメイン0.95以上が目安
            elif "MainScore" in resultAnalyzeData and resultAnalyzeData["MainScore"] != None and resultAnalyzeData["MainScore"] > 0.95:

                # メインもサブも0.95以上
                if "SubScore" in resultAnalyzeData and resultAnalyzeData["SubScore"] != None and resultAnalyzeData["SubScore"] > 0.95:
                    await replay_image_message(message, resultAnalyzeData["SubTagName"])
                    
                # サブだが0.8はある
                elif "SubScore" in resultAnalyzeData and resultAnalyzeData["SubScore"] != None and resultAnalyzeData["SubScore"] > 0.80:
                
                    await replay_image_message(message, resultAnalyzeData["SubTagName"], False)
                
                # メインが0.95以上ということでのみの評価
                else:
                    await replay_image_message(message, resultAnalyzeData["MainTagName"])
                    
            # まずはメイン0.8以上が最低ライン
            elif "MainScore" in resultAnalyzeData and resultAnalyzeData["MainScore"] != None and resultAnalyzeData["MainScore"] > 0.80:

                # メインもサブも0.95以上
                if "SubScore" in resultAnalyzeData and resultAnalyzeData["SubScore"] != None and resultAnalyzeData["SubScore"] > 0.95:
                    await replay_image_message(message, resultAnalyzeData["SubTagName"])

                elif "SubScore" in resultAnalyzeData and resultAnalyzeData["SubScore"] != None and resultAnalyzeData["SubScore"] > 0.80:
                
                    await replay_image_message(message, resultAnalyzeData["SubTagName"], False)

                # メインが0.8以上ということでのみの評価
                else:
                    await replay_image_message(message, resultAnalyzeData["MainTagName"], False)

            # まずはメイン0.6以上が最低ライン
            elif "MainScore" in resultAnalyzeData and resultAnalyzeData["MainScore"] != None and resultAnalyzeData["MainScore"] > 0.60:

                # メインもサブも0.98以上
                if "SubScore" in resultAnalyzeData and resultAnalyzeData["SubScore"] != None and resultAnalyzeData["SubScore"] > 0.98:
                    await replay_image_message(message, resultAnalyzeData["SubTagName"])

            
    except:
        print(sys.exc_info())
        
        
        
async def replay_image_message(message, word, isStrong = True):
    print("画像への返事")
    if isStrong:
        #await client.send_message(message.channel, word + " ですね！")
        await client.send_typing_message(message.channel, word + " ですね！")
        imgmsg = sm4.get_naturalchat_mesasge(message, word)
        #await client.send_message(message.channel, imgmsg)
        await client.send_typing_message(message.channel, imgmsg)
        await JapaneseOmikuji.get_omikuji_from_kaiwa(message, word)

    else:
        # await client.send_message(message.channel, "もしかしたら " + word + " ...ですか？")
        await client.send_typing_message(message.channel, "もしかしたら " + word + " ...ですか？")
        imgmsg = sm4.get_naturalchat_mesasge(message, word)
        await client.send_typing_message(message.channel, imgmsg)
        await JapaneseOmikuji.get_omikuji_from_kaiwa(message, word)

        
# 現在のunixタイムを出す
pre_datetime_unix_time = 0

def delete_old_image(message):

    global pre_datetime_unix_time

    # 現在のunixタイムを出す
    now = datetime.datetime.now()
    unix = now.timestamp()
    unix = int(unix)

    if unix-pre_datetime_unix_time > 600:

        pre_datetime_unix_time = unix

        files = os.listdir('DataTempImage')
        if len(files) > 1000:
            print("delete_old_image")
            for file in files:
                print(file)
                try:
                    m = re.search("^[0-9]+", file)
                    print(str(m))
                    date = m.group(0)
                    print(date)
                    date = int(date)
                    
                    # 現在のunixタイムを出す
                    now = datetime.datetime.now()
                    unix = now.timestamp()
                    unix = int(unix)

                    if unix-date > 600:
                        os.remove('DataTempImage/' + file)
                    # print (unix - date)
                    
                except:
                    print(sys.exc_info())
                

    else:
        print(unix-pre_datetime_unix_time)

