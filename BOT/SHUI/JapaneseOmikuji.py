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
import RegistEtherMemberInfo
import EastAsianWidthCounter


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
import copy


def get_data_inviteinfo_path():
    return "DataInviteInfo/InviteInfo.json"

def get_member_id_list(member):
    # メンバーIDのリスト一覧
    member_id_list = []
    for mem in list(member.server.members):
        member_id_list.append(mem.id)

    return member_id_list

def is_this_member_issue_member(member):
    print("who_invite_this_member")

    try:
        for mr in member.roles:
            if mr.name == "issue_inviter":
                return True

        member_id_list = {}
        for mem in list(member.server.members):
            member_id_list[mem.id] = mem

        path = get_data_inviteinfo_path()
        with open(path, "r") as fr:
            inviteinfo = json.load(fr)

        id = member.id
        for oneobj in inviteinfo.values():
            # childrenがあり
            if "children" in oneobj:
                # 今投稿したメンバーはそのchildrenにあるなら
                if id in oneobj["children"]:
                    # ownerがあるなら
                    if "owner" in oneobj:
                        if oneobj["owner"] in member_id_list:
                            owner_obj = member_id_list[ oneobj["owner"] ]
                            for r in owner_obj.roles:
                                if r.name == "issue_inviter":
                                    return True

        return False

    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))

        return False


def is_permission_omikuji_condition(message):
    ch = str(message.channel)
    if ch in ["★おみくじコーナー★"]:
       return True
#    if re.match("ディアたんと会話", ch) and (random.randint(1,10) < 3):
#       return True
       
    return False


def is_omikuji_command(text):
    if text == 'おみくじ' or text == 'みくじ' :
        return True

    okword_list = [
        'みくじ引いて', 'みくじを引いて',
        'みくじひいて', 'みくじをひいて',
        'みくじ引け', 'みくじを引け',
        'みくじひけ', 'みくじをひけ',
        'みくじ引く', 'みくじを引く',
        'みくじひく', 'みくじをひく',
        'みくじひく', 'みくじをひく',
        'みくじよろ', 'みくじをよろ',
        'みくじだよ',
        'みくじして', 'みくじをして',
        'みくじしよう', 'みくじをしよう',
        'みくじしよっか', 'みくじをしよっか',
        'みくじしろ', 'みくじをしろ',
        'みくじせよ', 'みくじをせよ',
        'みくじはよ', 'みくじをはよ',
        'みくじする', 'みくじをする',
        'みくじします', 'みくじをします',
        'みくじやろ', 'みくじをやろ',
        'みくじやって', 'みくじをやって',
        'みくじお願い', 'みくじをお願い',
        'みくじおねがい', 'みくじをおねがい',
    ]
    
    for ok_word in okword_list:
        if ok_word in text:
            return True
    
    return False



DirDataJapaneseOmikuji = "DataJapaneseOmikuji"

def get_date_omikuji_file(date):
    global DirDataJapaneseOmikuji
    fullpath = DirDataJapaneseOmikuji + "/" + date + ".txt"
    return fullpath
    
def is_exist_today_omikuji_file(date):
    fullpath = ""
    try:
        fullpath = get_date_omikuji_file(date)
        if os.path.exists(fullpath):
            return True
        else:
            return False
    except:
        pass
    
    return False

def get_today_omikuji_data(date):
    fullpath = get_date_omikuji_file(date)
    try:
        with open(fullpath,'r') as fr:
            json_data = json.load(fr)
        return json_data
    except:
        pass
        
    return False

def save_today_omikuji_data(date, dict):
    fullpath = get_date_omikuji_file(date)
    
    try:
        json_data = json.dumps(dict, indent=4)
        with open(fullpath,'w') as fw:
            fw.write(json_data)
        return True
    except:
        pass
    return False

def get_busy_omikuji_message(message):
    em = discord.Embed(title=" ", description="─────────\n" + message.author.display_name, color=0xDEED33)
    em.set_author(name='ディア', icon_url=client.user.default_avatar_url)
    em.set_author(name='ディア', icon_url='http://bdacoin.org/bot/omikuji/image/face.png')
    
    em.add_field(name="只今集計中です!!", value="─────────", inline=False)
    return em

def get_error_omikuji_message(message):
    em = discord.Embed(title=" ", description="─────────\n" + message.author.display_name, color=0xDEED33)
    em.set_author(name='ディア', icon_url=client.user.default_avatar_url)
    em.set_author(name='ディア', icon_url='http://bdacoin.org/bot/omikuji/image/face.png')
    
    em.add_field(name="エラーです!!", value="─────────", inline=False)
    return em



def get_today_datestring(message):
    #今日の日付の作成
    date = message.timestamp.now()
    strdate = str(date.year) + '{0:02d}'.format(date.month) + '{0:02d}'.format(date.day)
    return strdate

def is_busy_timestamp(message):
    #今日の日付の作成
    date = message.timestamp.now()
    if date.hour == 23 and date.minute == 59 and date.second >= 55:
        return True
    if date.hour == 0 and date.minute == 0 and date.second <= 5:
        return True
    
    return False

async def get_embedded_omikuji_object(message):

    has = await RegistEtherMemberInfo.has_member_data(message, message.author.id, True)
    print("メンバー情報がある？" + str(has))
    if not has:
        return
        
    member_exp = 0
    try:
        post_path = 'DataMemberPostInfo/' + str(message.author.id) + ".json"
        with open(post_path, "r") as fr:
            postinfo = json.load(fr)
            member_exp = postinfo["exp"]
    except:
        pass
    
    print("経験値" + str(member_exp))

    #今日の日付の作成
    date = message.timestamp.now()
    if is_busy_timestamp(message):
        return get_busy_omikuji_message(message)

    strdate = get_today_datestring(message)
    tstamp = message.timestamp.now()
    print(message.timestamp.now())

    # 今日はじめてで、ファイルが無いならファイル作成
    if not is_exist_today_omikuji_file(strdate):
        first_dict = {
            "date": strdate,
            "大吉": [],
            "吉": [],
            "中吉": [],
            "末吉": [],
            "ぴょん吉":[],
            "凶": []
        }

        result = save_today_omikuji_data(strdate, first_dict)
        if result == False:
            return get_error_omikuji_message(message)
    
    # ファイルがあるので読み込み
    result = get_today_omikuji_data(strdate)
    if result == False:
        return get_error_omikuji_message(message)
    
    un_list = {
        "大吉":"01",
        "吉":"02",
        "中吉":"03",
        "末吉":"04",
        "ぴょん吉":"07",
        "凶":"20"
    }
    
    # ハッシュからランダムで１つ選ぶ
    rndstr = random.choice(["吉", "吉", "吉", "吉", "吉", "中吉", "中吉", "中吉", "中吉", "中吉", "末吉", "末吉", "末吉", "末吉", "末吉", "大吉", "ぴょん吉", "凶"])
    
    # 問題があるメンバーであれば大吉は渡さない
    is_issue_member = is_this_member_issue_member(message.author)
    if is_issue_member or member_exp < 200:
        print("★問題のあるメンバー")
        rndstr = random.choice(["吉", "吉", "吉", "吉", "吉", "中吉", "中吉", "中吉", "中吉", "中吉", "末吉", "末吉", "末吉", "末吉", "末吉", "凶", "凶", "凶"])
    omikuji_key = rndstr
    omikuji_lv = un_list[rndstr]
    print("キ★" + omikuji_key)
    print("値★" + omikuji_lv)

    # 該当のメンバーはすでにおみくじを引いているかもしれない
    id = message.author.id
    is_exist = False
    today_omikuji = ""
    for k in result:
        print(k)
        if id in result[k]:
             today_omikuji = k
    
    is_use_ticket = False         
    # 該当のメンバーは今日おみくじを引いている
    if today_omikuji != "":
        print("今日すでに引いたのと同じものへと修正")
        omikuji_key = today_omikuji
        omikuji_lv = un_list[omikuji_key]
    
    # 該当のメンバーは今日はじめておみくじを引いた
    else:
        max_omikuji_payment_target = 10

        # 大吉以外で、かつ大吉を引いたメンツがまだ10人未満なら
        if omikuji_key!="大吉" and len(result["大吉"]) < max_omikuji_payment_target:
            # １つ幸運のおみくじ券を減らす
            omikuji_ticket_remain = await RegistEtherMemberInfo.decrement_one_member_omikuji_data(message, id)
            if omikuji_ticket_remain == None:
                print("幸運のおみくじが無い")
            else:
                print("幸運のおみくじを1枚引いた")
                # 再度振りなおし

                rndstr2 = random.choice(["吉", "吉", "吉", "中吉", "中吉", "中吉", "末吉", "末吉", "大吉", "ぴょん吉", "凶"])
                # 問題があるメンバーは大吉にならない
                if is_issue_member or member_exp < 200:
                    rndstr2 = random.choice(["吉", "吉", "吉", "中吉", "中吉", "中吉", "末吉", "末吉", "末吉", "凶", "凶"])
                omikuji_key2 = rndstr2
                omikuji_lv2 = un_list[rndstr2]

                is_use_ticket = True
                # より良い結果が出た
                if int(omikuji_lv2) < int(omikuji_lv):
                    print("おみくじの結果を上書き")
                    omikuji_key = omikuji_key2
                    omikuji_lv = omikuji_lv2

        # くじを引いたというユーザー記録を足す
        result[omikuji_key].append(id)
        save_today_omikuji_data(strdate, result)

    pyon_success = False
    if today_omikuji == "" and omikuji_key == "ぴょん吉":
        pyon_success = await RegistEtherMemberInfo.increment_one_member_omikuji_data(message, message.author.id)
        is_use_ticket = False
    # 
    em = discord.Embed(title=" ", description="─────────\n" + message.author.display_name + " さんの運勢は ...", color=0xDEED33)
#    em = discord.Embed(title=message.author.display_name + " さんの運勢", description=message.author.display_name + " さんの運勢は... __" + omikuji_key + "__ですよ!!", colour=0xDEED33)
    em.set_author(name='ディア', icon_url=client.user.default_avatar_url)
    em.set_author(name='ディア', icon_url='http://bdacoin.org/bot/omikuji/image/face.png')
    
    em.add_field(name=omikuji_key + "です!!", value="─────────", inline=False)
    if is_use_ticket:
        em.add_field(name="幸運のおみくじ券", value="１枚使用", inline=False)
    elif pyon_success:
        em.add_field(name="幸運のおみくじ券（よだれ付き）", value="１枚追加", inline=False)

    em.set_thumbnail(url="http://bdacoin.org/bot/omikuji/image/" + omikuji_lv + "_omkj.png")
    em.set_image(url="http://bdacoin.org/bot/omikuji/image/" + omikuji_lv + ".png")
    return em



async def say_embedded_omikuji_message(message):
    if is_omikuji_command(message.content):
        em = await get_embedded_omikuji_object(message)
        if em != None:
            await client.send_message(message.channel, embed=em)

        # 簡易だと以下だがデザイン性には欠ける
        # await client.send_message(message.channel, str(message.author.display_name) + "さんの運勢だよ!")
        # img_list = [ "01.png", "02.png", "03.png", "04.png", "05.png" ]

        # １つランダムで選ぶ
        # path = random.choice(img_list)

        # 該当チャンネルに投稿する
        # await client.send_file(message.channel, path)


# 会話からおみくじを得る
async def get_omikuji_from_kaiwa(message, override_message = ""):
    stripped_msg = message.content.strip()
    if override_message:
        stripped_msg = override_message
    
    #utf8_byte 数
    kaiwa_utf8_byte_count = EastAsianWidthCounter.get_east_asian_width_count_effort(stripped_msg)
    print("文字列のバイト数" + str(kaiwa_utf8_byte_count))
    # 一定以上の長さは100と評価する
    if kaiwa_utf8_byte_count > 50:
         kaiwa_utf8_byte_count = 50

    # 最大でも100/1000 即ち10％
    rnd = random.randint(1, 300)
    if rnd < kaiwa_utf8_byte_count:
        try:
            success = await RegistEtherMemberInfo.increment_one_member_omikuji_data(message, message.author.id)
            # 実際に枚数が増えているならば
            if success != None:
                if rnd % 3 == 0:
                    await client.send_message(message.channel, "<@" + message.author.id + "> さん、これ落ちてましたよ！")
                if rnd % 3 == 1:
                    await client.send_message(message.channel, "このおみくじ券、<@" + message.author.id + "> さんのですか？")
                if rnd % 3 == 2:
                    await client.send_message(message.channel, "<@" + message.author.id + "> さん、おみくじ券いかがですか～")
                    
                em = discord.Embed(title=" ", description=" ", color=0xDEED33)
                em.add_field(name="幸運のおみくじ券", value="１枚追加", inline=False)
                await client.send_message(message.channel, embed=em)
            
                print("おみくじ1枚ゲット!!")
        except:
            print(sys.exc_info())



def is_report_command_condition(command):
    if re.match("^!omikujiinfo \d{8}$", command):
        return True


def report_command_one_key_name(json_data, key, message):

    member_id_list = []
    for mem in list(message.channel.server.members):
        member_id_list.append(mem.id)

    msg = []
    try:
        for id in json_data[key]:
            if id in member_id_list:
                msg.append( "<@" + str(id) + ">" )
    except:
        pass

    return " , ".join(msg)

def report_command_one_key_eth(json_data, key, message):

    member_id_list = []
    for mem in list(message.channel.server.members):
        member_id_list.append(mem.id)

    msg = []
    
    try:
        for id in json_data[key]:
            if id in member_id_list:
                fullpath = "DataMemberInfo/" + str(id) + ".json"
                if os.path.exists(fullpath):
                    try:
                        with open(fullpath,'r') as fr:
                            json_data = json.load(fr)
                        msg.append(json_data["eth_address"])
                        
                    except:
                        pass
                        
                else:
                    msg.append( "<@" + str(id) + ">" )
    except:
        pass

    return '[ "' + '" , "'.join(msg) + '" ]'

async def report_command(message):
    if is_report_command_condition(message.content):
        m = re.search("^!omikujiinfo (\d{8})$", message.content)
        date = m.group(1)
        fullpath = get_date_omikuji_file(date)
        if os.path.exists(fullpath):
            json_data = get_today_omikuji_data(date)
            ret = report_command_one_key_name(json_data, "大吉", message)
            await client.send_message(message.channel, ret)
            ret = report_command_one_key_eth(json_data, "大吉", message)
            await client.send_message(message.channel, ret)
        else:
            await client.send_message(message.channel, "指定の年月日のおみくじ情報はありません。")
        

