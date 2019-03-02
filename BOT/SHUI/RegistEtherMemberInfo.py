# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Akitsugu Komiyama
# under the GPL v3 License.
#

import builtins

import re
import json
import types
import base64
import os
import sys
import datetime
import time
import glob
import discord
import traceback

import WalletAddressDeleter

if False:
    client: discord.Client = discord.Client()


async def report_error(message, error_msg):
    em = discord.Embed(title=" ", description="─────────\n" , color=0xDEED33)
    avator_url = client.user.avatar_url or client.user.default_avatar_url
    avator_url = avator_url.replace(".webp?", ".png?")
    em.set_author(name='朱伊', icon_url=avator_url)

    em.add_field(name="返信相手", value= "<@" + message.author.id + ">", inline=False)
    em.add_field(name="エラー", value=error_msg, inline=False)
    print("ここまできた1")
    try:
        print(error_msg)
        print("ここまできた２")
        await client.send_message(message.channel, embed=em)
    except Exception as e:
        print("ここまできた３")
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        print(sys.exc_info())

def get_data_memberinfo_path(message: discord.Message, id: str):
    return 'DataMemberInfo/' + str(id) + ".json"

def get_data_memberpaid_path(message: discord.Message, id: str):
    return 'DataMemberPaid/' + str(id) + ".json"

def get_data_ticketinfo_path(message: discord.Message, id: str):
    return 'DataTicketInfo/' + str(id) + ".json"


async def decrement_one_member_omikuji_data(message: discord.Message, id: str):
    try:
        has = await has_member_data(message, id, False)
        if not has:
            print("has_member_dataない")
            return None

        path = get_data_ticketinfo_path(message, id)
        print("get_data_ticketinfo_path" + path)
        with open(path, "r") as fr:
            memberinfo = json.load(fr)

        if memberinfo["omikuji_ticket_count"] <= 0:
            print("おみくじのチケットが無い")
            return None

        memberinfo["omikuji_ticket_count"] = memberinfo["omikuji_ticket_count"] - 1

        path = get_data_ticketinfo_path(message, id)
        json_data = json.dumps(memberinfo, indent=4)
        with open(path, "w") as fw:
            fw.write(json_data)

        print("チケットカウントを返す" + str(memberinfo["omikuji_ticket_count"]))
        return memberinfo["omikuji_ticket_count"]

    except:
        await report_error(message, "decrement_one_member_omikuji_data中にエラー")
        await report_error(message, sys.exc_info())

    return None

# 1枚増やすが、５枚以上は増えない。又1枚増えると、６時間は増えない
async def increment_one_member_omikuji_data(message: discord.Message, id: str):

    try:
        has = await has_member_data(message, id, False)
        if not has:
            print("has_member_dataない")
            return None

        path = get_data_ticketinfo_path(message, id)
        print("get_data_ticketinfo_path" + path)
        with open(path, "r") as fr:
            memberinfo = json.load(fr)

        # そんなにもっていても仕方がない
        if memberinfo["omikuji_ticket_count"] >= 5:
            return None

        memberinfo["omikuji_ticket_count"] = memberinfo["omikuji_ticket_count"] + 1

        # 現在のunixタイムを出す
        now = datetime.datetime.now()
        unix = now.timestamp()
        unix = int(unix)

        # すでに過去の記録があるならば…(初版ではこのデータ型はないのでチェックが必要)
        if "omikuji_ticket_last_gettime" in memberinfo:
            # 過去のunixタイムを過去のnow形式にする。
            old_unix = memberinfo["omikuji_ticket_last_gettime"]
            old_now = datetime.datetime.fromtimestamp(old_unix)
            tdelta = now - old_now
            total_seconds = tdelta.total_seconds()
            print("差分:" + str(total_seconds))
            if total_seconds < 60 * 60 * 8: # 8時間に1枚が限界とする。1日3枚まで。
                print("短すぎる")
                return None

            memberinfo["omikuji_ticket_last_gettime"] = unix

        # はじめての保存なら、問題はないさっくり保存
        else:
            memberinfo["omikuji_ticket_last_gettime"] = unix

        path = get_data_ticketinfo_path(message, id)
        json_data = json.dumps(memberinfo, indent=4)
        with open(path, "w") as fw:
            fw.write(json_data)

        print("チケットカウントを返す" + str(memberinfo["omikuji_ticket_count"]))
        return memberinfo["omikuji_ticket_count"]

    except:
        await report_error(message, "increment_one_member_omikuji_data中にエラー")
        await report_error(message, sys.exc_info())

    return None

async def get_count_one_member_omikuji_data(message: discord.Message, id: str):
    try:
        has = await has_member_data(message, id, False)
        if not has:
            return 0

        path = get_data_ticketinfo_path(message, id)
        print(path)
        with open(path, "r") as fr:
            memberinfo = json.load(fr)

        return memberinfo["omikuji_ticket_count"]

    except:
        await report_error(message, "get_count_one_member_omikuji_data中にエラー")
        await report_error(message, sys.exc_info())

    return None


async def update_one_member_data(message: discord.Message, address: str, id: str) -> bool:
    try:

        path = get_data_memberinfo_path(message, id)
        print(path)
        with open(path, "r") as fr:
            memberinfo = json.load(fr)

        memberinfo["eth_address"] = address

        path = get_data_memberinfo_path(message, id)
        json_data = json.dumps(memberinfo, indent=4)
        with open(path, "w") as fw:
            fw.write(json_data)
        return True

    except:
        await report_error(message, "MemberDataデータ作成中にエラー")
        await report_error(message, sys.exc_info())

    return False

# 1人分のメンバーデータの作成
async def make_one_member_data(message: discord.Message, address: str, id: str) -> bool:
    try:
        memberinfo = {
            "eth_address": "",
            "waves_address": "",
            "user_id": 0
        }

        memberinfo["user_id"] = id
        memberinfo["eth_address"] = address

        path = get_data_memberinfo_path(message, id)
        print(path)
        json_data = json.dumps(memberinfo, indent=4)
        with open(path, "w") as fw:
            fw.write(json_data)

        return await make_one_ticketinfo_data(message, address, id)

    except:
        await report_error(message, "make_one_member_data 中にエラーが発生しました。")
        await report_error(message, sys.exc_info())
    return False


async def make_one_ticketinfo_data(message: discord.Message, address: str, id: str) -> bool:
    try:
        ticketinfo = {
            "omikuji_ticket_count": 0,
            "user_id": 0
        }

        ticketinfo["user_id"] = id
        ticketinfo["omikuji_ticket_count"] = 1

        path = get_data_ticketinfo_path(message, id)
        print(path)
        json_data = json.dumps(ticketinfo, indent=4)
        with open(path, "w") as fw:
            fw.write(json_data)

        return True
    except:
        await report_error(message, "make_one_ticketinfo_data 中にエラーが発生しました。")
        await report_error(message, sys.exc_info())
    return False



async def make_one_member_paid(message: discord.Message, id: str) -> bool:
    try:
        paidinfo = {
            "kaiwa_paid_lv": 0,
            "blog_paid_lv": 0,
            "invite_paid_lv": 0,
            "twitter_paid_lv": 0,
            "facebook_paid_lv": 0,
            "kaiwa_paid_amount": 0,
            "blog_paid_amount": 0,
            "twitter_paid_amount": 0,
            "facebook_paid_amount": 0,
            "invite_paid_amount": 0,
            "user_id": 0
        }

        paidinfo["user_id"] = id

        path = get_data_memberpaid_path(message, id)
        print(path)
        json_data = json.dumps(paidinfo, indent=4)
        with open(path, "w") as fw:
            fw.write(json_data)
        return True
    except:
        await report_error(message, "make_one_member_paid 中にエラーが発生しました。")
        await report_error(message, sys.exc_info())

    return False


async def regist_one_member_data(message: discord.Message, id: str):

    address = message.content.strip()
    # イーサアドレス登録だ
    if WalletAddressDeleter.is_message_ether_pattern(address):
        try:
            # すでに登録済みである
            path = get_data_memberinfo_path(message, id)
            if (os.path.exists(path)):
                # 更新
                await update_one_member_data(message, address, id)
            # 存在しなかった時にやる
            else:
                await make_one_member_data(message, address, id)

            path = get_data_memberpaid_path(message, id)
            if (os.path.exists(path)):
                # 何もしない
                pass
            # 存在しなかった時にやる
            else:
                await make_one_member_paid(message, id)

            await show_one_member_data(message, id)

        except:
            print("regist_one_member_data でエラー")
            print(sys.exc_info())

    # イーサアドレス登録だ
    elif WalletAddressDeleter.is_message_waves_pattern(address):
        await report_error(message, "wavesウォレットのアドレスではなく、\nETHウォレットのアドレスを投稿してください。")
    else:
        await report_error(message, "イーサアドレスのパターンではありません。")
        return

def is_regist_one_member_data_condition(message: discord.Message) -> bool:
    if message.channel == get_ether_regist_channel(message):
        print("イーサアドレス登録")
        return True

    print("イーサアドレスちゃんねるにマッチしない")
    return False


def get_ether_regist_channel(message: discord.Message) -> discord.Channel:
    for ch in message.channel.server.channels:
        if "お財布登録" in str(ch) or "eth-address" in str(ch):
            return ch

    return None


async def show_another_member_data(message: discord.Message):
    print("another_member_data_show_command")
    try:
        m = re.search(r"^!memberinfo <@(\d+?)>$", message.content)
        if m:
            print("マッチ")
            targetg_member_id = m.group(1)
            if targetg_member_id:
                print("サーバー")
                svr = message.author.server
                target_author = svr.get_member(targetg_member_id)
                print("おーさー" + str(target_author))
                if target_author:
                    await show_one_member_data(message, target_author.id)

    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        pass


async def show_another_ticket_data(message: discord.Message):
    print("another_ticket_data_show_command")
    try:
        m = re.search(r"^!ticketinfo <@(\d+?)>$", message.content)
        if m:
            print("マッチ")
            targetg_member_id = m.group(1)
            if targetg_member_id:
                print("サーバー")
                svr: discord.Server = message.author.server
                target_author: discord.User = svr.get_member(targetg_member_id)
                print("おーさー" + str(target_author))
                if target_author:
                    await show_one_ticket_data(message, target_author.id)

    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        pass



async def show_one_member_data(message: discord.Message, id: str) -> bool:
    try:
        path = get_data_memberinfo_path(message, id)
        has = await has_member_data(message, id, True)
        print("メンバー情報がある？" + str(has))
        if not has:
            return

        print(path)
        with open(path, "r") as fr:
            memberinfo = json.load(fr)

        path = get_data_memberpaid_path(message, id)
        print(path)
        with open(path, "r") as fr:
            paidinfo = json.load(fr)

        em = discord.Embed(title="", description="", color=0xDEED33)
        author: discord.Member = message.server.get_member(id)
        avator_url = None
        if author:
            avator_url = author.avatar_url or author.default_avatar_url
        else:
            avator_url = message.author.default_avatar_url
        print(avator_url)
        avator_url = avator_url.replace(".webp?", ".png?")
        em.set_thumbnail(url=avator_url)
        em.add_field(name="メンバー情報", value="<@" + id + ">", inline=False)
        em.add_field(name="ETHウォレットのアドレス", value=memberinfo["eth_address"], inline=False)


        try:
            await client.send_message(message.channel, embed=em)
        except:
            print(sys.exc_info())

        return True

    except:
        await report_error(message, "show_one_member_data中にエラー")
        await report_error(message, sys.exc_info())

    return False


async def show_one_ticket_data(message: discord.Message, id: str):
    try:
        path = get_data_ticketinfo_path(message, id)
        has = await has_member_data(message, id, True)
        print("メンバー情報がある？" + str(has))
        if not has:
            return

        print(path)
        with open(path, "r") as fr:
            ticketinfo = json.load(fr)

        em = discord.Embed(title="", description="", color=0xDEED33)
        author: discord.Member = message.server.get_member(id)
        avator_url = None
        if author:
            avator_url = author.avatar_url or author.default_avatar_url
        else:
            avator_url = message.author.default_avatar_url
        print(avator_url)
        avator_url = avator_url.replace(".webp?", ".png?")
        em.set_thumbnail(url=avator_url)
        em.add_field(name="チケット情報", value="<@" + id + ">", inline=False)
        em.add_field(name="幸運のおみくじ券", value=str(ticketinfo["omikuji_ticket_count"]) + " 枚", inline=False)


        try:
            await client.send_message(message.channel, embed=em)
        except:
            print(sys.exc_info())

        return True

    except:
        await report_error(message, "show_one_member_data中にエラー")
        await report_error(message, sys.exc_info())

    return False



def is_show_one_member_data_condition(message: discord.Message) -> bool:
    msg = str(message.content).strip()
    if "!memberinfo" == msg:
        return True

    return False


def is_show_another_member_data_condition(message: discord.Message) -> bool:
    msg = str(message.content).strip()
    if re.match(r"^!memberinfo <@\d+?>$", msg):
        return True


def is_show_one_ticket_data_condition(message: discord.Message) -> bool:
    msg = str(message.content).strip()
    if "!ticketinfo" == msg:
        return True

    return False


def is_show_another_ticket_data_condition(message: discord.Message) -> bool:
    msg = str(message.content).strip()
    if re.match(r"^!ticketinfo <@\d+?>$", msg):
        return True



async def has_member_data(message: discord.Message, id: str, withMessage: bool) -> bool:
    path = get_data_memberinfo_path(message, id)
    if not os.path.exists(path):
        if withMessage:
            ch: discord.Channel = get_ether_regist_channel(message)
            await report_error(message, "登録情報がありません。\n" + "<#" + ch.id + ">" + " に\nご自身の **MyEtherWallet** など、\nエアドロが受け取れるETHウォレットアドレスを投稿し、\n**コインを受け取れるように**してください。")
        return False
    else:
        return True

