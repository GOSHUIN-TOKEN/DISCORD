#coding: utf-8
# ver 2.1
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
import traceback
import discord

import WalletAddressDeleter

async def report_error(message, error_msg):
    em = discord.Embed(title=" ", description="─────────\n" , color=0xDEED33)
    em.set_author(name='Dia', icon_url=client.user.default_avatar_url)
    em.set_author(name='Dia', icon_url='http://bdacoin.org/bot/omikuji/image/face.png')
    
    em.add_field(name="返信相手(Reply)", value= "<@" + message.author.id + ">", inline=False)
    em.add_field(name="エラー(Error)", value=error_msg, inline=False)
    try:
        print(error_msg)
        await client.send_message(message.channel, embed=em)
    except:
        print(sys.exc_info())

def get_data_memberinfo_path(message, id):
    return 'AirdropMemberInfo/' + str(id) + ".json"

def get_data_memberpaid_path(message, id):
    return 'AirdropMemberPaid/' + str(id) + ".json"



async def update_one_member_data(message, address, id):
    try:
        has_address = await is_has_address(message, address, id)
        if has_address:
            await report_error(message, "そのイーサアドレスは別アカウントの人に登録されています。\n(That Ether wallet address is registered by another account.")
            return False

        path = get_data_memberinfo_path(message, id)
        print(path)
        with open(path, "r") as fr:
            memberinfo = json.load(fr)

        memberinfo["eth_address"] = address

        path = get_data_memberinfo_path(message, id)
        json_data = json.dumps(memberinfo, indent=4)
        with open(path, "w") as fw:
            fw.write(json_data)
            
        await update_all_member_data(message, memberinfo)
            
        return True

    except:
        await report_error(message, "Error while creating MemberData data.")
        await report_error(message, sys.exc_info())
    
    return False


async def is_has_address(message, address, id):
    try:

        path = "AirdropMemberInfo/AirdropMemberInfoList.json"
        with open(path, "r") as fr:
            allinfo = json.load(fr)
        # print(allinfo)
        for key in allinfo:
            memberinfo = allinfo[key]
            # 別人なのに同一のイーサアドレスが投稿されようとしている
            if memberinfo["eth_address"] == address and int(memberinfo["user_id"]) != int(id):
                return True
            
        return False

    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        await report_error(message, "Error while judge is_has_address.")
        await report_error(message, sys.exc_info())
    
    return False


async def update_all_member_data(message, memberinfo):
    try:

        path = "AirdropMemberInfo/AirdropMemberInfoList.json"
        print(path)
        with open(path, "r") as fr:
            allinfo = json.load(fr)

        allinfo[memberinfo["user_id"]] = memberinfo

        path = "AirdropMemberInfo/AirdropMemberInfoList.json"
        json_data = json.dumps(allinfo, indent=4)
        with open(path, "w") as fw:
            fw.write(json_data)
            
        return True

    except:
        await report_error(message, "Error while creating Update_all_member_data.")
        await report_error(message, sys.exc_info())
    
    return False


# 1人分のメンバーデータの作成
async def make_one_member_data(message, address, id):
    try:
        has_address = await is_has_address(message, address, id)
        if has_address:
            await report_error(message, "そのイーサアドレスは別アカウントの人に登録されています。\n(That Ether wallet address is registered by another account.")
            return False
            
        memberinfo = {
            "eth_address": "",
            "user_id": 0
        }
        
        memberinfo["user_id"] = id

        memberinfo["eth_address"] = address
        
        path = get_data_memberinfo_path(message, id)
        print(path)
        json_data = json.dumps(memberinfo, indent=4)
        with open(path, "w") as fw:
            fw.write(json_data)
            
        await update_all_member_data(message, memberinfo)
            
        return True
    except:
        await report_error(message, "An error occurred during make_one_member_data.")
        await report_error(message, sys.exc_info())
    return False


async def make_one_member_paid(message, id):
    try:
        paidinfo = {
            "airdrop_201809": 0,
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
        await report_error(message, "An error occurred during make_one_member_paid.")
        await report_error(message, sys.exc_info())
    
    return False


async def regist_one_member_data(message, id):

    address = message.content.strip()
    # イーサアドレス登録だ
    if WalletAddressDeleter.is_message_ether_pattern(address):
        try:
            # すでに登録済みである
            path = get_data_memberinfo_path(message, id)
            if (os.path.exists(path)):
                # 何もしない
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
            print("Error in regist_one_member_data")
            print(sys.exc_info())

    # イーサアドレス登録だ
    elif WalletAddressDeleter.is_message_waves_pattern(address):
        await report_error(message, "wavesウォレットのアドレスではなく、\n**ETHウォレット**のアドレスを投稿してください。\n(Please post the address of **Ether wallet** address, not the address of Waves one.)")
    else:
        await report_error(message, "イーサアドレスのパターンではありません。\n(The post is not a pattern of Ether wallet address.)")
        return

def is_regist_one_member_data_condition(message):
    if message.channel == get_ether_regist_channel(message):
        return True

    return False


def get_ether_regist_channel(message):
    for ch in message.channel.server.channels:
        if "regist-airdrop-eth" in str(ch):
            return ch
            
    return None



async def show_one_member_data(message, id):
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
        avator_url = message.author.avatar_url or message.author.default_avatar_url
        print(avator_url)
        avator_url = avator_url.replace(".webp?", ".png?")
        em.set_thumbnail(url=avator_url)
        em.add_field(name="エアドロ登録情報(Airdrop Registration Information)", value="<@" + id + ">", inline=False)
        em.add_field(name="ETHウォレットのアドレス(Ether Wallet Address)", value=memberinfo["eth_address"], inline=False)


        try:
            await client.send_message(message.channel, embed=em)
        except:
            print(sys.exc_info())

        return True

    except:
        await report_error(message, "Error in show_one_member_data.")
        await report_error(message, sys.exc_info())
    
    return False



def is_show_one_member_data_condition(message):
    msg = str(message.content).strip()
    if "!airdropinfo" == msg:
        return True

    return False



async def has_member_data(message, id, withMessage):
    path = get_data_memberinfo_path(message, id)
    if not os.path.exists(path):
        if withMessage:
            ch = get_ether_regist_channel(message)
            await report_error(message, "登録情報がありません。ご自身の **MyEtherWallet** など、\nエアドロが受け取れるETHウォレットアドレスを投稿し、\n**コインを受け取れるように**してください。\n(There is no your registration information. \n Please post your Ether wallet address such as your own MyEtherWallet, so that you can receive BLACK DIA COINs.)")
        return False
    else:
        return True
        
