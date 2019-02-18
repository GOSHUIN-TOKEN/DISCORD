# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Akitsugu Komiyama
# under the GPL v3 License.
#


import discord

from typing import Union, List, Dict, Tuple

if False:
    client: discord.Client = discord.Client()

def is_mic_permission_condition(message: discord.Message) -> bool:
    return str(message.channel) in ["📢朱伊のマイク"]


def say_mic_message(message: discord.Message) -> Tuple[discord.Channel, str]:

    all_message = message.content
    message_list = all_message.split("\n")

    if len(message_list) < 2:
        print("投稿文章は条件を満たさず")
        return "", ""

    target_channel_name = message_list[0]
    target_channel_name = target_channel_name.strip()
    msg = "\n".join(message_list[1:])

    target_channel_id = ""
    for ch in message.server.channels:
        if str("<#" + ch.id + ">") == str(target_channel_name):
            target_channel_id = ch.id

    print("マイク対象のチャンネルIDは:" + str(target_channel_id) )

    if target_channel_id == "":
        return None, ""

#    print(msg)
    target_channel = discord.Object(id=target_channel_id)
#    print(str(target_channel))
    return target_channel, msg


async def say_message(message: discord.Message):
    target_channel, msg = say_mic_message(message)
    if target_channel != None and msg != "":
        await client.send_message(target_channel, msg)

    # if message.attachments != None:
        # path = message.attachments[0]["url"]
        # await client.send_file(message.channel, path)
