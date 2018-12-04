import builtins

import re
import random
import requests
import json
import types
import base64
import os
import traceback
import sys, datetime, time
import discord
import EnvironmentVariable


# パッケージのインポートとインスタンス作成
client = discord.Client()

# 他のモジュールへの伝搬が面倒なので、Pythonの組み込み変数同様の扱いにしてしまう
builtins.client = client


# テストサーバー用のトークン
BOT_TOKEN = EnvironmentVariable.get_discord_bot_token()



# ログイン&準備が完了したら一度だけ実行される
@client.event
async def on_ready():
    # コンソールにBOTとしてログインした名前とUSER-IDを出力
    print('Logged in as')
    print('BOT-NAME :', client.user.name)
    print('BOT-ID   :', client.user.id)
    print('------')



def get_bdr_top_holders_html(p):
    try:
        res = requests.get('https://etherscan.io/token/generic-tokenholders2?a=0xf6caa4bebd8fab8489bc4708344d9634315c4340&s=0&p=1')
        res.raise_for_status()
        return res.text
    except:
        return None



def get_all_member_id_and_ether_bind_data():
    dict_data = {}
    dirlist = os.listdir("./DataMemberInfo")
    # print(dirlist)
    for j in dirlist:
        path = "./DataMemberInfo/" + j
        try:
            with open(path, "r") as fr:
                memberinfo = json.load(fr)
                m_add = memberinfo["eth_address"].lower()
                m_id = memberinfo["user_id"]
                dict_data[m_add] = m_id
        except:
            print("Error")
            pass
    
    return dict_data


def get_member_top_holder_info():
    html = get_bdr_top_holders_html(1)
    # print(html)
    ret_list = re.findall("<tr><td>(\d+)</td><td><span><a href='/token/0xf6caa4bebd8fab8489bc4708344d9634315c4340\?a=(0x.+?)' target='_parent'>0x.+?</a></span></td><td>(\d+)</td><td>\d+%</td></tr>", html)
    # イーサアドレスを小文字に統一する
    for ix in range(0, len(ret_list)):
        ret_list[ix] = [int(ret_list[ix][0].lower()), ret_list[ix][1].lower(), float(ret_list[ix][2].lower())]
    # イーサアドレス(小文字)がキー、値がユーザーIDの辞書を取得
    dict_data = get_all_member_id_and_ether_bind_data()
    
    
    top_holder_info = {}
    # ホルダー一覧で
    for holder in ret_list:
        #順位
        rank = holder[0]
        # イーサアドレス(小文字)
        eadd = holder[1]
        # ホールド量
        amount = holder[2]
        try:
            # イーサアドレスに紐づいたユーザーIDがあるなら
            if eadd in dict_data:
                # print( str(dict_data[eadd]) + ":" + str(amount))
                top_holder_info[dict_data[eadd]] = {"eth_address":eadd, "amount":amount}
        except:
            print("error")
            pass
    
    return top_holder_info
    # print(ret_list)

ROLE_NAME_TOP_HOLDER_1000 = "ホールド1000万枚～"

async def add_top_holder_role(roles, author, holder_info):
    global ROLE_NAME_TOP_HOLDER_1000
    
    # そのサーバーが持ってる役職
    roles_list = roles
    for r in roles_list:
        try:
            #print(r.name)
            # 役職の名前そのものに必須到達レベルがある。
            if r.name == ROLE_NAME_TOP_HOLDER_1000:
                await client.add_roles(author, r)
                print("付与した" + r.name)
        except Exception as e:
            t, v, tb = sys.exc_info()
            print(traceback.format_exception(t,v,tb))
            print(traceback.format_tb(e.__traceback__))

async def remove_top_holder_role(roles, author):
    global ROLE_NAME_TOP_HOLDER_1000

    # 現在トップホルダーの役職もってる？
    has_top_roles = False
    for ar in author.roles:
        if ar.name == ROLE_NAME_TOP_HOLDER_1000:
            has_top_roles = True
            
    # もってないなら削除はするまでもない
    if not has_top_roles:
        return
        
    # そのサーバーが持ってる役職
    roles_list = roles
    for r in roles_list:
        try:
            if r.name == ROLE_NAME_TOP_HOLDER_1000:
                await client.remove_roles(author, r)
                print("ホールド役所削除した" + r.name)
        except Exception as e:
            t, v, tb = sys.exc_info()
            print(traceback.format_exception(t,v,tb))
            print(traceback.format_tb(e.__traceback__))


def get_today_datestring(message):
    #今日の日付の作成
    date = message.timestamp.now()
    strdate = str(date.year) + '{0:02d}'.format(date.month) + '{0:02d}'.format(date.day)
    return strdate


LAST_TOPHOLDER_UPDATE_DATESTRING = "-"

# メッセージを受信するごとに実行される
@client.event
async def on_message(message):
    try:
        global LAST_TOPHOLDER_UPDATE_DATESTRING
        
        # 日付が変わったていたら
        todaystr = get_today_datestring(message)
        if todaystr != LAST_TOPHOLDER_UPDATE_DATESTRING:
            print("日付変わった")
            LAST_TOPHOLDER_UPDATE_DATESTRING = todaystr
        else:
            print("日付同じ")
            return
        

        top_holder_info = get_member_top_holder_info()
        for m2 in list(message.channel.server.members):
            id = m2.id
            try:
                print(m2.name)
                if id in top_holder_info:
                    print("idあり")
                    holder_info = top_holder_info[id]
                    if holder_info["amount"] > 10000000: #1000万枚以上
                        print("以上")
                        await add_top_holder_role(message.channel.server.roles, m2, holder_info)
                    else:
                        # 削除
                        await remove_top_holder_role(message.channel.server.roles, m2)
                else:
                    # 削除
                    await remove_top_holder_role(message.channel.server.roles, m2)
                    
            except Exception as e:
                t, v, tb = sys.exc_info()
                print(traceback.format_exception(t,v,tb))
                print(traceback.format_tb(e.__traceback__))

    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))


# APP(BOT)を実行
client.run(BOT_TOKEN)



