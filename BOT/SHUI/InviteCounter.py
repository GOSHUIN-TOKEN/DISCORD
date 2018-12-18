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
import copy
import RegistEtherMemberInfo


def get_welcome_count_channel(member):
    for ch in member.server.channels:
        if "🌳裏門🌳" == str(ch):
            return ch
            
    return None

def get_welcome_channel(member):
    for ch in member.server.channels:
        if "🌳裏門🌳" == str(ch):
            return ch
            
    return None


def get_data_inviteinfo_path():
    return "DataInviteInfo/InviteInfo.json"

# https://foolean.net/p/1691

# User.created_at
# Returns the user’s creation time in UTC.
# This is when the user’s discord account was created.
USER_ID_LIST = {}


async def on_member_join(member):
    print("on_member_join")

    try:
        path = get_data_inviteinfo_path()
        with open(path, "r") as fr:
            inviteinfo = json.load(fr)

        this_member_inviter = 0

        # サーバーにある招待オブジェクトリスト
        invites = await client.invites_from(member.server)
        # print(invites)
        for invite in invites:

            # 招待状の期限が無限でないものは考慮外
            if invite.max_age != 0:
                continue

            # print(invite)

            # すでに存在するが、
            if not invite.id in inviteinfo:
                # 追加
                inviteinfo[invite.id] = {"uses":invite.uses, "owner":invite.inviter.id, "children":[]}

            # 前回の使用者数と食い違っている
            
            invitehash = inviteinfo[invite.id]
            # print("invite.uses" + str(invite.uses))
            # print("invitehash['uses']" + str(invitehash["uses"]))
            if invite.uses != invitehash["uses"]:

                invitehash["uses"] = invite.uses

                _inviter = invite.inviter

                # print("これが使われた" + _inviter.id + ":" + _inviter.name)
                if not "children" in invitehash:
                    invitehash["children"] = []
                
                # メンバーIDがまだそこに追加されてなければ
                if not member.id in invitehash["children"]:
                    # このメンバーが、招待された人としてIDを追加する
                    invitehash["children"].append(member.id)
                    this_member_inviter = _inviter
                    break
                    

            invitehash["uses"] = invite.uses

        path = get_data_inviteinfo_path()
        json_data = json.dumps(inviteinfo, indent=4)
        with open(path, "w") as fw:
            fw.write(json_data)

        ch = get_welcome_count_channel(member)
        msg_content = "新規参加者の識別ID:" + member.id +":"+ "<@"+member.id +">\n"
        if this_member_inviter != 0:
            msg_content = msg_content + "└この人を招待した人:" + "<@"+this_member_inviter.id +">" + "\n"

        await client.send_message(ch, msg_content)

        ch2 = get_welcome_channel(member)
        msg_content = "新規参加者:" + member.name + "\n"
        if this_member_inviter != 0:
            msg_content = msg_content + "└この人を招待した人:" + this_member_inviter.name + "\n"

        await client.send_message(ch2, msg_content)
        
        # キャッシュにuserオブジェクトの方を追加。userオブジェクトは
        # サーチが重いのでこまめにキャッシュしておく
        _mem_user = await client.get_user_info(member.id)
        if _mem_user:
            USER_ID_LIST[member.id] = _mem_user

    except:
        pass


def get_member_id_list(member):
    # メンバーIDのリスト一覧
    member_id_list = []
    for mem in list(member.server.members):
        member_id_list.append(mem.id)

    return member_id_list

def get_member_id_hash(member):
    # メンバーIDのリスト一覧
    member_id_hash = {}
    for mem in list(member.server.members):
        member_id_hash[mem.id] = mem

    return member_id_hash
    
async def on_member_remove(member):

    try:
        member_id_list = get_member_id_list(member)
    
        path = get_data_inviteinfo_path()
        with open(path, "r") as fr:
            inviteinfo = json.load(fr)

        this_member_inviter = 0
            
        # その中をなめまわして、該当のメンバーがいるなら削除
        for key in inviteinfo:
            invitehash = inviteinfo[key]
            if not "children" in invitehash:
                invitehash["children"] = []
        
            # メンバーIDが配列にあるならば
            if member.id in invitehash["children"]:
                # このメンバーが、退場した人としてIDを削除する
                invitehash["children"].remove(member.id)
                try:
                    _user = await client.get_user_info(invitehash["owner"])
                    # print("招待者のユーザーオブジェクト:" + str(_user))
                    this_member_inviter = _user
                except Exception as e:
                    t, v, tb = sys.exc_info()
                    print(traceback.format_exception(t,v,tb))
                    print(traceback.format_tb(e.__traceback__))
                    pass
            
            # リストの中で削除するので、複製を作ってfor
            for child in invitehash["children"][:]:
                if not child in member_id_list:
                    # もうこの人はサーバーに居ない
                    print("元々サーバーに居ない")
                    invitehash["children"].remove(child)


        # サーバーにある招待オブジェクトリスト
        invites = await client.invites_from(member.server)
        # print(invites)
        for invite in invites:
            # 招待状の期限が無限でないものは考慮外
            if invite.max_age != 0:
                continue

            # print(invite)
            _inviter = invite.inviter

            # すでに存在するが、
            if not invite.id in inviteinfo:
                # 追加
                inviteinfo[invite.id] = {"uses":invite.uses, "owner":_inviter.id, "children":[]}
            else:
                # カウント数を最新に
                inviteinfo[invite.id]["uses"] = invite.uses
            
        path = get_data_inviteinfo_path()
        json_data = json.dumps(inviteinfo, indent=4)
        with open(path, "w") as fw:
            # print("保存した")
            fw.write(json_data)

        ch = get_welcome_count_channel(member)
        msg_content = "退場者の識別ID:" + member.id +":"+ "<@"+member.id +">\n"
        if this_member_inviter != 0:
            msg_content = msg_content + "└この人を招待した人" + "<@"+this_member_inviter.id +">" + "\n"

        await client.send_message(ch, msg_content)

        ch2 = get_welcome_channel(member)
        msg_content = "退場者:" + member.name + "\n"
        if this_member_inviter != 0:
            msg_content = msg_content + "└この人を招待した人:" + this_member_inviter.name + "\n"

        await client.send_message(ch2, msg_content)

    except:
        pass
            


def is_invites_show_command_condition(command):
    if re.match("^!invites$", command):
        return True

def is_another_invites_show_command_condition(command):
    print(command)
    if re.match("^!invites <@\d+?>$", command):
        return True


async def another_invites_show_command(message):
    print("another_invites_show_command")
    try:
        m = re.search("^!invites <@(\d+?)>$", message.content)
        if m:
            print("マッチ")
            targetg_member_id = m.group(1)
            if targetg_member_id:
                print("サーバー")
                svr = message.author.server
                target_author = svr.get_member(targetg_member_id)
                print("おーさー" + str(target_author))
                if target_author:
                    await invites_show_command(message, target_author)

    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        pass




async def invites_show_command(message, target_author):
    print("invites_show_command")
    owner_id = target_author.id
    
    is_issue_inviter = False
    for r in target_author.roles:
        if r.name == "issue_inviter":
            is_issue_inviter = True
    
    try:
        invite_point = 0
        invite_num   = 0
        
        path = get_data_inviteinfo_path()
        with open(path, "r") as fr:
            inviteinfo = json.load(fr)

        # 現存するサーバーのメンツ
        member_id_hash = get_member_id_hash(target_author)

        # それぞれの招待について
        for key in inviteinfo:
            invitehash = inviteinfo[key]
        
            # 招待の発行主が一致した
            if "owner" in invitehash and owner_id == invitehash["owner"]:

                # そのURLを使って招待された人がいる
                if "children" in invitehash:

                    # 招待された人それぞれが…
                    for child_id in invitehash["children"]:

                        # サーバーに居る人なら
                        if child_id in member_id_hash:
                            member_obj = member_id_hash[child_id]
                            
                            _user = None
                            # メンバーオブジェクト⇒ユーザーオブジェクトへ
                            if child_id in USER_ID_LIST:
                                _user = USER_ID_LIST[child_id]
                            
                            if _user == None:
                                _user = await client.get_user_info(child_id)
                                USER_ID_LIST[child_id] = _user
                            
                            # アカウント作成時期
                            create_time = _user.created_at

                            # 現在のunixタイムを出す
                            now_time = datetime.datetime.now()

                            tdelta = now_time - create_time
                            total_seconds = tdelta.total_seconds()

                            invite_num = invite_num + 1
                            add_point = 1
                            
                            
                            # 20日以上経過していること
                            if tdelta and tdelta.days >= 20:
                                
                                # print("差分:" + str(tdelta.days))
                                # print("差分:" + str(total_seconds))
                                
                                add_point = 1
                            else:
                                add_point = 0.1
                            
                            
                            memberinfo_path = RegistEtherMemberInfo.get_data_memberinfo_path(message, child_id)
                            if memberinfo_path and os.path.exists(memberinfo_path):
                                add_point = add_point * 1
                                # print("メンバー登録情報あり")
                                # print(memberinfo_path)
                            else:
                                add_point = add_point * 0.5
                                # print("メンバー登録情報なし")

                            if is_issue_inviter:
                                add_point = add_point * 0.1

                            invite_point = invite_point + add_point


        em = discord.Embed(title="", description="", color=0xDEED33)
        avator_url = target_author.avatar_url or target_author.default_avatar_url
        print(avator_url)
        avator_url = avator_url.replace(".webp?", ".png?")
        em.set_thumbnail(url=avator_url)
        em.add_field(name="招待情報", value="<@" + owner_id + ">", inline=False)
        em.add_field(name="招待評価点", value=str(round(invite_point, 2)) + " 点", inline=True)
        # em.add_field(name="現存招待数 (参考値)", value=str(invite_num) + " 個", inline=True)
        try:
            await client.send_message(message.channel, embed=em)
        except:
            print(sys.exc_info())

    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        pass



def is_another_invitesraw_show_command_condition(command):
    print(command)
    if re.match("^!invitesraw <@\d+?>$", command):
        return True


async def another_invitesraw_show_command(message):
    print("another_invitesraw_show_command")
    try:
        m = re.search("^!invitesraw <@(\d+?)>$", message.content)
        if m:
            print("マッチ")
            targetg_member_id = m.group(1)
            if targetg_member_id:
                print("サーバー")
                svr = message.author.server
                target_author = svr.get_member(targetg_member_id)
                print("おーさー" + str(target_author))
                if target_author:
                    await invitesraw_show_command(message, target_author)

    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        pass



# User.created_at
# Returns the user’s creation time in UTC.
# This is when the user’s discord account was created.

async def invitesraw_show_command(message, target_author):
    print("invites_show_command")
    owner_id = target_author.id
    try:
        invite_point = 0
        invite_num   = 0
        
        path = get_data_inviteinfo_path()
        with open(path, "r") as fr:
            inviteinfo = json.load(fr)

        # 現存するサーバーのメンツ
        member_id_hash = get_member_id_hash(target_author)

        # それぞれの招待について
        for key in inviteinfo:
            invitehash = inviteinfo[key]
        
            # 招待の発行主が一致した
            if "owner" in invitehash and owner_id == invitehash["owner"]:

                # そのURLを使って招待された人がいる
                if "children" in invitehash:

                    # 招待された人それぞれが…
                    for child_id in invitehash["children"]:

                        # サーバーに居る人なら
                        if child_id in member_id_hash:
                            member_obj = member_id_hash[child_id]
                            
                            # メンバーオブジェクト⇒ユーザーオブジェクトへ
                            # _user = await client.get_user_info(child_id)
                            
                            # アカウント作成時期
                            create_time = member_obj.joined_at

                            # 現在のunixタイムを出す
                            now_time = datetime.datetime.now()

                            tdelta = now_time - create_time
                            total_seconds = tdelta.total_seconds()

                            invite_num = invite_num + 1
                            add_point = 1
                            # 20日以上経過していること
                            if tdelta and tdelta.days >= 20:
                                
                                # print("差分:" + str(tdelta.days))
                                # print("差分:" + str(total_seconds))
                                
                                add_point = 1
                            else:
                                add_point = 0.1
                            
                            
                            memberinfo_path = RegistEtherMemberInfo.get_data_memberinfo_path(message, child_id)
                            if memberinfo_path and os.path.exists(memberinfo_path):
                                add_point = add_point * 1
                                # print("メンバー登録情報あり")
                                # print(memberinfo_path)
                            else:
                                add_point = add_point * 0.5
                                # print("メンバー登録情報なし")

                            invite_point = invite_point + add_point


        em = discord.Embed(title="", description="", color=0xDEED33)
        avator_url = target_author.avatar_url or target_author.default_avatar_url
        print(avator_url)
        avator_url = avator_url.replace(".webp?", ".png?")
        em.set_thumbnail(url=avator_url)
        em.add_field(name="招待情報", value="<@" + owner_id + ">", inline=False)
        em.add_field(name="招待評価点", value=str(round(invite_point, 2)) + " 点", inline=True)
        # em.add_field(name="現存招待数 (参考値)", value=str(invite_num) + " 個", inline=True)
        try:
            await client.send_message(message.channel, embed=em)
        except:
            print(sys.exc_info())

    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        pass

