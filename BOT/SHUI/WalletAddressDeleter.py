#coding: utf-8
# ver 2.1

# 正規表現
import re

# Wavesアドレスはダメなチャンネル
nopermit_channnel_of_waves_address = ["^雑談$", "^english.$", "ルーレット.+", "^botでランクを確認$", "^★おみくじコーナー.+", "^ロゴ投稿場", "^招待人数確認", "^bdaチャート"]

# Etherアドレスはダメなチャンネル
nopermit_channnel_of_ether_address = ["^雑談$", "^english.$", "ルーレット.+", "^botでランクを確認$", "^★おみくじコーナー.+", "^ロゴ投稿場", "^招待人数確認", "^bdaチャート", "^新規の方のみairdrop", "^new-people-only-airdrop",]

# Wavesウォレットのアドレスのパターン
def is_message_waves_pattern(message):
    message = message.strip();
    if len(message) != 35:
        return False

    if re.match("^(\s*)3P[0-9a-zA-Z]+(\s*)$", message):
        return True
    
    return False
    
# Etherウォレットのアドレスのパターン
def is_message_ether_pattern(message):
    message = message.strip();
    if len(message) != 42:
        return False

    if re.match("^(\s*)0x[0-9a-zA-Z]+(\s*)$", message):
        return True
    
    return False


def is_nopermit_waves_channel(channel_name):
    cn_name = str(channel_name)
    # wavesアドレスが許されないチャンネルのいずれかか？
    for pattern in nopermit_channnel_of_waves_address:
        if re.match(pattern, cn_name):
            return True

    return False

def is_nopermit_ether_channel(channel_name):
    cn_name = str(channel_name)
    # etherアドレスが許されないチャンネルのいずれかか？
    for pattern in nopermit_channnel_of_ether_address:
        if re.match(pattern, cn_name):
            return True

    return False


async def violation_wallet_address_message(message):

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
