#coding: utf-8
# ver 2.1
import builtins
import ctypes
import re
import random
import requests
import json
import types
import base64
import os
import sys, datetime, time
import discord

import EnvironmentVariable
import ChatLevelUp

Kernel32 = ctypes.windll.Kernel32

def get_docomo_naturalchat_key():
    KEY = os.getenv("DISCORD_DOCOMO_NATURALCHAT_KEY", r'')
    appid_01 = os.getenv("DISCORD_DOCOMO_NATURALCHAT_APPID_01", r'')
    appid_02 = os.getenv("DISCORD_DOCOMO_NATURALCHAT_APPID_02", r'')
    appid_03 = os.getenv("DISCORD_DOCOMO_NATURALCHAT_APPID_03", r'')
    appid_04 = os.getenv("DISCORD_DOCOMO_NATURALCHAT_APPID_04", r'')
    appid_05 = os.getenv("DISCORD_DOCOMO_NATURALCHAT_APPID_05", r'')
    return {"KEY":KEY, "appid_01":appid_01, "appid_02":appid_02, "appid_03":appid_03, "appid_04":appid_04, "appid_05":appid_05}


class NaturalChatMessage:
    """自然対話用のクラス"""

    def __init__(self, KEY, appid):
        self.KEY = KEY
        self.appid = appid
        self.lastMode = "dialog"
        self.appear_zatsudan_count = 0

    def get_naturalchat_mesasge(self, message, override_word = "", need_lock = True):
        KEY = self.KEY
        
        mutex = None
        try:

            #エンドポイントの設定
            endpoint = 'https://api.apigw.smt.docomo.ne.jp/naturalChatting/v1/dialogue?APIKEY=REGISTER_KEY' #変更
            url = endpoint.replace('REGISTER_KEY', KEY)
            appid = self.appid

            norm_nickname = self.get_normalized_nickname(message.author.display_name)
            # print(norm_nickname)

            date = datetime.datetime.now()
            datastr = date.strftime("%Y-%m-%d %H:%M:%S")

            text = message.content
            if override_word:
                text = override_word

            if need_lock:
                print(appid)
                mutex = Kernel32.CreateMutexA(0, 1, appid)
                result = Kernel32.WaitForSingleObject(mutex, 2000)   # ロック解除されるまで待つ
                if result == 0x00000102:
                    print("ロック待ちエラー")
                    return "う～ん..."
            
            payload = {'language':'ja-JP', 'botId':'Chatting','appId':appid,'voiceText':text, 
                "clientData":{
                      "option":{
                        "nickname":norm_nickname,
                        "sex":"女",
                        "mode":self.lastMode,
                        "t":""
                      }
                  },
                  "appRecvTime": datastr,
                  "appSendTime": datastr
            }

            # print(payload)
            # payload = {'botId':'Chatting','appKind':"Smart Phone"} #変更

            headers = {'Content-type': 'application/json'}

            #送信
            r = requests.post(url, data=json.dumps(payload), headers=headers)
            
            data = r.json()
            # print(data)
            response = data['systemText']['utterance'] #変更
            command = data['command']
            self.lastMode = base64.b64decode( command ).decode('utf-8')
            
            if 'srtr' in self.lastMode:
                self.lastMode = 'srtr'
            else:
                self.lastMode = 'dialog'
            
            msg = ""
            if response =="読みが不明か名詞ではありませんので、別の言葉でお願いします。" and (not "しりとり" in text):
                # 必ず矯正してから
                sm5.lastMode = "dialog"
                # 一般の返答を挟む
                response = sm5.get_naturalchat_mesasge(message, "", False)
                # メッセージのチャンネルに対応したキャッシュにたしこむ
                if message.channel.id in ChatLevelUp.update_kaiwa_post_hasu:
                    ChatLevelUp.update_kaiwa_post_hasu[message.channel.id].append(response)

                msg = response

                
            else:
                response = self.modify_response(response)
                # メッセージのチャンネルに対応したキャッシュにたしこむ
                if message.channel.id in ChatLevelUp.update_kaiwa_post_hasu:
                    ChatLevelUp.update_kaiwa_post_hasu[message.channel.id].append(response)

                msg = '{0.author.mention} '.format(message) + response

            
            if mutex != None:
                Kernel32.ReleaseMutex(mutex)
                Kernel32.CloseHandle(mutex)

            return msg
            
        except RuntimeError:
            if mutex != None:
                Kernel32.ReleaseMutex(mutex)
                Kernel32.CloseHandle(mutex)

            print(RuntimeError)
            return "今ディア調子が悪いみたい..."


    def get_normalized_nickname(self, nickname):
        #会話の入力
        norm_nickname = ""
        for c in nickname:
            str = c + ''
            l = len(str.encode('utf8'))
            if (l) < 4: # 拡張領域文字だとDoCoMoの方が扱えない
                norm_nickname += str
        
        return norm_nickname
        
    # レスポンス結果の修正
    def modify_response(self, response):
        #シリトリモードだと一人称が変になるので強引に修正
        if self.lastMode == 'srtr':
            response = response.replace("ボクの勝ち", "ディアの勝ち")
            response = response.replace("ぼくの勝ち", "ディアの勝ち")
            response = response.replace("ボクの負け", "ディアの負け")
            response = response.replace("ぼくの負け", "ディアの負け")
            response = response.replace("ぼくから", "ディアから")
            response = response.replace("ボクから", "ディアから")

        # 年齢は共通で上書き
        response = response.replace("年齢は、26歳", "年齢は、21歳")
        
        return response

    def get_lastmode(self):
        return self.lastMode
        
    def decrement_appear_zatsudan_cnt(self, msg):

        # ディアタンは自分の名前を呼ばれるとしばらくは雑談に登場を継続する
        if "Diatan" in msg:
            self.appear_zatsudan_count = 5
        if "ディアたん" in msg:
            self.appear_zatsudan_count = 4
        if "ディア" in msg:
            self.appear_zatsudan_count = 3
            
        # すでに居ない時は、ごくまれに登場する
        if self.appear_zatsudan_count < -1:
            if random.randint(1,30) < 2:
                self.appear_zatsudan_count = 2

        # しりとりモードになっている時は、登場状態を継続する
        if self.get_lastmode() == "srtr":
            self.appear_zatsudan_count = 3
        
        # １回引く
        self.appear_zatsudan_count = self.appear_zatsudan_count - 1

        return self.appear_zatsudan_count



def CreateObject():
    params = get_docomo_naturalchat_key()
    sm1 = NaturalChatMessage(params["KEY"], params["appid_01"])
    sm2 = NaturalChatMessage(params["KEY"], params["appid_02"])
    sm3 = NaturalChatMessage(params["KEY"], params["appid_03"])
    sm4 = NaturalChatMessage(params["KEY"], params["appid_04"])
    sm5 = NaturalChatMessage(params["KEY"], params["appid_05"])
    return sm1, sm2, sm3, sm4, sm5



def NaturalChattableChannelRegex():
    return ["^雑談$", "^ディアたんと会話", "^ボットと雑談", "^★おみくじコーナー★"]