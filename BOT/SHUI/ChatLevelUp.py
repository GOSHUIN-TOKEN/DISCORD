# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Akitsugu Komiyama
# under the GPL v3 License.
#

import unicodedata
import difflib

import builtins

import re
import json
import os
import sys, datetime, time
import traceback
import discord
import emoji

import RegistEtherMemberInfo

import EastAsianWidthCounter

if False:
    client: discord.Client = discord.Client()

LV_GET_COIN_TABLE: list = [
    [5,5000,],
    [10,17000,],
    [15,28000,],
    [20,51000,],
    [25,83000,],
    [30,124000,],
    [35,176000,],
    [40,240000,],
    [45,318000,],
    [50,409000,],
    [55,516000,],
    [60,640000,],
    [65,782000,],
    [70,942000,],
    [75,1122000],
    [80,1324000],
    [85,1548000],
    [90,1795000],
    [95,2066000],
    [100,2500000]
]

# そのレベルになるのに必要な総経験値(Mee6と同じ計算式)
def need_experiment_value(level) -> int:
    xp_to_desired_level = 5 / 6 * level * (2 * level * level + 27 * level + 91)
    return xp_to_desired_level


LV_TO_EXP_LIST = []
def createChatLevelUpTable() -> None:
    if len(LV_TO_EXP_LIST) ==0:
        # lv200まで埋める
        for lv in range(0, 201):
            LV_TO_EXP_LIST.append([lv, need_experiment_value(lv)])

    # print(LV_TO_EXP_LIST)


def get_lv_from_exp(exp: int) -> int:
    lv = 0
    for t in LV_TO_EXP_LIST:
        # 指定された経験値より、レベル表の総合経験値が低いなら
        if t[1] < exp:
            lv = t[0] # すくなくともそのレベルには到達している

    return lv

# ２つのテキストの類似度の比較
def get_sequence_matcher_coef(test_1: str, text_2: str) -> float:

    # unicodedata.normalize() で全角英数字や半角カタカナなどを正規化する
    normalized_str1: str = unicodedata.normalize('NFKC', test_1)
    normalized_str2: str = unicodedata.normalize('NFKC', text_2)

    # 類似度を計算、0.0~1.0 で結果が返る
    s = difflib.SequenceMatcher(None, normalized_str1, normalized_str2).ratio()
    # print( "match ratio:" + str(s))
    return s


async def report_error(message: discord.Message, error_msg: str):
    print(message, error_msg)
    em = discord.Embed(title=" ", description="─────────\n" , color=0xDEED33)
    avator_url: str = client.user.default_avatar_url or client.user.default_avatar_url
    avator_url: str = avator_url.replace(".webp?", ".png?")
    em.set_author(name='朱伊', icon_url=avator_url)

    em.add_field(name="返信相手", value= "<@" + message.author.id + ">", inline=False)
    em.add_field(name="エラー", value=error_msg, inline=False)
    try:
        print(error_msg)
        await client.send_message(message.channel, embed=em)
    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))


def get_data_kaiwa_post_path(message: discord.Message) -> str:
    id = message.author.id
    return 'DataMemberPostInfo/' + str(id) + ".json"


def has_post_data(message: discord.Message) -> bool:
    path: str = get_data_kaiwa_post_path(message)
    if not os.path.exists(path):
        return False
    else:
        return True





async def is_syougou_up(message: discord.Message):
    pass


async def show_level_infomation(message: discord.Message, exp: int, default="会話レベル情報"):

    paidinfo: dict = None
    try:
        path: str = RegistEtherMemberInfo.get_data_memberpaid_path(message, message.author.id)
        print(path)
        with open(path, "r") as fr2:
            paidinfo = json.load(fr2)
    except:
        pass

    try:
        lv: int = get_lv_from_exp(exp)
        em = discord.Embed(title="", description="", color=0xDEED33)
        em.add_field(name=default, value= "<@" + message.author.id + ">", inline=False)

        avator_url: str = message.author.avatar_url or message.author.default_avatar_url
        avator_url: str = avator_url.replace(".webp?", ".png?")

        try:
            if message.content == "!rankinfo":
                if paidinfo != None and "kaiwa_paid_lv" in paidinfo and "kaiwa_paid_amount" in paidinfo:
                    if paidinfo["kaiwa_paid_amount"] != 0 and sum(paidinfo["kaiwa_paid_amount"].values()) > 0:
                        max_level_YM = max(paidinfo["kaiwa_paid_lv"].keys())
                        print(max_level_YM)
                        em.add_field(name="報酬を支払済みの Lv", value=str((paidinfo["kaiwa_paid_lv"][max_level_YM] // 5) * 5), inline=True)
                        em.add_field(name="報酬を支払済みの GOSHUIN枚数", value=str(max(paidinfo["kaiwa_paid_amount"].values())) + " 枚", inline=True)
                    else:
                        em.add_field(name="報酬を支払済みの GOSHUIN枚数", value="0 枚", inline=True)
                else:
                    em.add_field(name="報酬を支払済みの GOSHUIN枚数", value="0 枚", inline=True)

        except Exception as e3:
            t, v, tb = sys.exc_info()
            print(traceback.format_exception(t,v,tb))
            print(traceback.format_tb(e3.__traceback__))
            print("報酬を支払済み 中エラー")

        # em.set_author(name=" ", icon_url=avator_url)
        em.add_field(name="Lv", value=str(lv), inline=True)
        amari: int = exp-LV_TO_EXP_LIST[lv][1]
        nnext: int = LV_TO_EXP_LIST[lv+1][1]-LV_TO_EXP_LIST[lv][1]
        str_cur_per_nex: str = str(int(amari)) + "/" + str(int(nnext)) + " EX"
        int_cur_per_nex: int = int(amari / nnext * 200)
        if int_cur_per_nex < 0:
            int_cur_per_nex = 0
        if int_cur_per_nex > 200:
            int_cur_per_nex = 200
        em.add_field(name="経験値", value=str_cur_per_nex, inline=True)
        em.set_thumbnail(url=avator_url)

        em.set_image(url="http://discord.goshuin.in/BOT/ChatLevelUp/image/level_up_image_{0:03d}.png".format(int_cur_per_nex))
    #        em.add_field(name="テスト", value=avator_url, inline=True)

        await client.send_message(message.channel, embed=em)
    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        print("show_level_infomation 中エラー")

async def command_show_level_infomation(message: discord.Message, author: discord.Member):

    try:
        if not has_post_data(message):
            await make_one_kaiwa_post_data(message)

        path: str = get_data_kaiwa_post_path(message)
        print(path)
        with open(path, "r") as fr:
            postinfo: dict = json.load(fr)

        await show_level_infomation(message, postinfo["exp"])

    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        print("show_level_infomation 中エラー")

def is_level_command_condition(message: discord.Message) -> bool:
    if re.match("^!rankinfo$", message):
        return True
    if re.match("^!rank$", message):
        return True

    return False


async def add_level_role(roles, author: discord.Member, level: int):
    # そのサーバーが持ってる役職
    roles_list = roles
    for r in roles_list:
        try:
            #print(r.name)
            # 役職の名前そのものに必須到達レベルがある。
            m = re.search(r".+\s*LV(\d+)", r.name, re.IGNORECASE)
            if m:
                #print("マッチ" + r.name)
                roles_lv = m.group(1)
                if roles_lv and int(roles_lv) <= level:
                    # print("付与開始" + r.name)
                    await client.add_roles(author, r)
                    print("付与した" + r.name)
        except Exception as e:
            t, v, tb = sys.exc_info()
            print(traceback.format_exception(t,v,tb))
            print(traceback.format_tb(e.__traceback__))

async def all_member_add_level_role(message: discord.Message):
    for m in list(message.channel.server.members):

        id: str = m.id
        path = 'DataMemberPostInfo/' + str(id) + ".json"
        try:
            if os.path.exists(path):
                with open(path, "r") as fr:
                    postinfo: dict = json.load(fr)
                    post_level: int = get_lv_from_exp(postinfo["exp"])
                    await add_level_role(message.channel.server.roles, m, post_level)
        except Exception as e:
            t, v, tb = sys.exc_info()
            print(traceback.format_exception(t,v,tb))
            print(traceback.format_tb(e.__traceback__))



# 繰り返し対処用。反復を圧縮する
def hanpukuword_to_onceword(text: str) -> str:
    ma = re.search(r"(.{2,30})(\1){1,50}", text)
    if ma:
        result = text.replace(ma.group(0), ma.group(1))
        # print("0"+ma.group(0))
        # print("1"+ma.group(1))
        # print("2"+ma.group(2))
        return result
    else:
        return text

# 絵文字を除去
def remove_emoji(src_str: str) -> str:
    ret_str = ""

    # 正規表現パターンを構築
    emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
                            "]+", flags=re.UNICODE)

    ret_str = emoji_pattern.sub(r':emj:', src_str)
    #for c in src_str:
    #    if c in emoji.UNICODE_EMOJI:
    #        ret_str += ":emj:"
    #    else:
    #        ret_str += c

    rgx = r'<[a-z0-9]?:[a-zA-Z0-9_\-]+:[0-9]{5,30}>'
    while(True):
        ma = re.search(rgx, ret_str)
        if ma:
            ret_str = re.sub(rgx, ":emj:", ret_str)
        else:
            break

    ret_str = ret_str.replace("\n", "")
    return ret_str

# 投稿を各チャンネルで保持
update_kaiwa_post_hasu: dict = {}

async def update_one_kaiwa_post_data(message: discord.Message):

    try:
        # print("キャッシュ")
        # print(update_kaiwa_post_hasu)

        if not has_post_data(message):
            await make_one_kaiwa_post_data(message)

        # まだそのチャンネルの履歴キャッシュがないならば
        if not message.channel.id in update_kaiwa_post_hasu:
            # 用意
            update_kaiwa_post_hasu[message.channel.id] = []

        path = get_data_kaiwa_post_path(message)
        print(path)
        with open(path, "r") as fr:
            postinfo = json.load(fr)

        # ゴミ除去
        text: str = message.content.strip()

        print("元:" + text)
        try:
            # まぁ5回ぐらいでええやろ…
            text = remove_emoji(text)
            for iix in range(0, 6):
                text = hanpukuword_to_onceword(text)
        except:
            pass
        print("後:" + text)

        # 経験値の加算係数を出す
        minimum_coef: float = 1
        # 過去の20投稿との比較で最低の係数を出す（類似したものがあるほど係数が低くなる)
        for hist in postinfo["posthistory"]:
            temp_coef: float = 1 - get_sequence_matcher_coef(hist.replace("\n", ""), text.replace("\n", ""))
            # print("どうか:" + str(temp_coef) + hist + ", " + text)
            if temp_coef < minimum_coef:
                minimum_coef = temp_coef

        # 過去の該当チャンネルの履歴との比較
        for hist in update_kaiwa_post_hasu[message.channel.id]:
            temp_coef = 1 - get_sequence_matcher_coef(hist.replace("\n", ""), text.replace("\n", ""))
            # print("どうか:" + str(temp_coef) + hist + ", " + text)
            if temp_coef < minimum_coef:
                minimum_coef = temp_coef

        print("最低係数:" + str(minimum_coef))

        base_experience: int = 60
        add_experience: int = int(minimum_coef * base_experience)
        if add_experience < 0:
            add_experience = 0

        # そのテキストのutf8バイト数を超えないようにする
        kaiwa_utf8_byte_count: int = EastAsianWidthCounter.get_east_asian_width_count_effort(text)
        # 6バイトまでは判定しない
        if kaiwa_utf8_byte_count <= 6:
            kaiwa_utf8_byte_count = 0
        if add_experience > kaiwa_utf8_byte_count:
            add_experience = kaiwa_utf8_byte_count

        # 添付ファイルがあるのであれば、下駄を40はかせる
        attach_list = message.attachments
        if len(attach_list) > 0:
            add_experience = add_experience + 40

        # 投稿差分タイムを越えないようにする
        # 現在のunixタイムを出す
        now = datetime.datetime.now()
        unix = now.timestamp()
        unix = int(unix)

        # すでに過去の記録があるならば…(初版ではこのデータ型はないのでチェックが必要)
        if "post_last_gettime" in postinfo:
            # 過去のunixタイムを過去のnow形式にする。
            old_unix = postinfo["post_last_gettime"]
            old_now = datetime.datetime.fromtimestamp(old_unix)
            tdelta = now - old_now
            total_seconds = tdelta.total_seconds()
            print("差分:" + str(total_seconds))
            if "見ちゃイヤ" in message.channel.name:
                if add_experience > total_seconds/10:
                    print("差分タイム/15へと抑え込み:" + str(total_seconds/10)) 
                    add_experience = int(total_seconds/8)
            # 普通のチャンネル
            else:
                if add_experience > total_seconds/2:
                    print("差分タイム/2へと抑え込み:" + str(total_seconds/2)) 
                    add_experience = int(total_seconds/2)

            postinfo["post_last_gettime"] = unix

        # はじめての保存なら、問題はないさっくり保存
        else:
            postinfo["post_last_gettime"] = unix


        prev_level = get_lv_from_exp(postinfo["exp"])

        # 朱伊と会話だったらレベルに応じて上限を抑えてしまう
        if "朱伊と会話" in message.channel.name and prev_level > 0:
            if add_experience > (100/prev_level):
                 add_experience = int(100/prev_level)
                 print(str(100/prev_level) + "へと抑え込み")

        postinfo["exp"] = postinfo["exp"] + add_experience
        post_level = get_lv_from_exp(postinfo["exp"])
        if prev_level != post_level:
            await show_level_infomation(message, postinfo["exp"], "会話レベルがアップしました!!")
            await add_level_role(message.channel.server.roles, message.author, post_level)


        print(str(add_experience) + "が経験値として加算された")

        # テキストも履歴として加える
        postinfo["posthistory"].append(text)

        # 多くなりすぎていれば削除。
        # 3回ぐらい繰り返しておけば十分か
        for rng in [0, 1, 2, 4, 5]:
            # すでに本人の履歴が20以上あれば
            if len(postinfo["posthistory"]) > 20:
                # 先頭をカット
                postinfo["posthistory"].pop(0)

            # すでに該当チャンネルの投稿履歴が500以上あれば
            if len(update_kaiwa_post_hasu[message.channel.id]) > 500:
                # 先頭をカット
                update_kaiwa_post_hasu[message.channel.id].pop(0)


        print("ただいまのレベル" + str(get_lv_from_exp(postinfo["exp"])))

        path = get_data_kaiwa_post_path(message)
        json_data = json.dumps(postinfo, indent=4)
        with open(path, "w") as fw:
            fw.write(json_data)

        if kaiwa_utf8_byte_count > 6:
            # メッセージのチャンネルに対応したキャッシュにたしこむ
            update_kaiwa_post_hasu[message.channel.id].append(text)

        return postinfo

    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        await report_error(message, "update_one_kaiwa_post_dataデータ作成中にエラー")
        await report_error(message, sys.exc_info())

    return None


# 1人分のメンバーデータの作成
async def make_one_kaiwa_post_data(message: discord.Message):
    try:
        postinfo = {
            "user_id": message.author.id,
            "posthistory": [],
            "exp": 0,
        }

        path = get_data_kaiwa_post_path(message)
        print("ここきた★" + path)
        json_data = json.dumps(postinfo, indent=4)
        with open(path, "w") as fw:
            fw.write(json_data)
        return postinfo
    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        await report_error(message, "make_one_kaiwa_post_data 中にエラーが発生しました。")
        await report_error(message, sys.exc_info())
    return None



async def push_kaiwa_post(message: discord.Message, text: str):

    postinfo = await update_one_kaiwa_post_data(message)
    if postinfo != None:
        pass

    # count = EastAsianWidthCounter.get_east_asian_width_count_effort(text)
    # print(count)

# テスト
if __name__ == '__main__':
    mesage = {"content": "スパスパゲッティ", "id": 3333333333}
    push_kaiwa_post(mesage, "")
    push_kaiwa_post(mesage, "aaaaaa")


