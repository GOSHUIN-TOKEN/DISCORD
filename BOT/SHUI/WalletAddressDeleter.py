# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Akitsugu Komiyama
# under the GPL v3 License.
#

# 正規表現
import re
import discord

from typing import Union, List, Dict, Tuple

if False:
    client: discord.Client = discord.Client()

# Wavesアドレスはダメなチャンネル
nopermit_channnel_of_waves_address: List[str] = ["^雑談$", "^english.$", "ルーレット.+", "^botでランクを確認$", "^★おみくじコーナー.+", "^ロゴ投稿場", "^招待人数確認", "^bdaチャート"]

# Etherアドレスはダメなチャンネル
nopermit_channnel_of_ether_address: List[str]= ["^雑談$", "^english.$", "ルーレット.+", "^botでランクを確認$", "^★おみくじコーナー.+", "^ロゴ投稿場", "^招待人数確認", "^bdaチャート", "^新規の方のみairdrop", "^new-people-only-airdrop",]

# Wavesウォレットのアドレスのパターン
def is_message_waves_pattern(message: str) -> bool:
    message = message.strip()
    if len(message) != 35:
        return False

    if re.match(r"^(\s*)3P[0-9a-zA-Z]+(\s*)$", message):
        return True

    return False

# Etherウォレットのアドレスのパターン
def is_message_ether_pattern(message) -> bool:
    message = message.strip()
    if len(message) != 42:
        return False

    if re.match(r"^(\s*)0x[0-9a-zA-Z]+(\s*)$", message):
        return True

    return False


def is_nopermit_waves_channel(channel_name: str) -> bool:
    cn_name = str(channel_name)
    # wavesアドレスが許されないチャンネルのいずれかか？
    for pattern in nopermit_channnel_of_waves_address:
        if re.match(pattern, cn_name):
            return True

    return False

def is_nopermit_ether_channel(channel_name: str) -> bool:
    cn_name = str(channel_name)
    # etherアドレスが許されないチャンネルのいずれかか？
    for pattern in nopermit_channnel_of_ether_address:
        if re.match(pattern, cn_name):
            return True

    return False


async def violation_wallet_address_message(message: discord.Message) -> bool:

    is_delete = False

    if is_nopermit_waves_channel(message.channel):
        if is_message_waves_pattern(message.content):
            is_delete = True
            await client.delete_message(message)
            # await client.send_message(message.channel, "Wavesアドレス検知。アドレス投稿が許されないチャンネルです")

    if is_nopermit_ether_channel(message.channel):
        if is_message_ether_pattern(message.content):
            await client.delete_message(message)
            is_delete = True
            # await client.send_message(message.channel, "Etherアドレス検知。アドレス投稿が許されないチャンネルです")

    return is_delete
