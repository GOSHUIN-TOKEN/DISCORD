#coding: utf-8
# ver 2.1


import discord



def is_mic_permission_condition(message):
    return str(message.channel) in ["ディアたんのマイク"]


def say_mic_message(message):

    all_message = message.content
    message_list = all_message.split("\n")
    
    if len(message_list) < 2:
        return "", ""
        
    target_channel_name = message_list[0]
    target_channel_name = target_channel_name.strip()
    msg = "\n".join(message_list[1:])

    target_channel_id = ""
    for ch in message.server.channels:
#        print("ターゲット名" + target_channel_name)
#        print("チャンネル名" + "<#" + ch.id + ">")
        if str("<#" + ch.id + ">") == str(target_channel_name):
            target_channel_id = ch.id

#    target_channel = discord.Object(id='12324234183172')
    if target_channel_id == "":
        return "", ""
        
#    print(msg)
    target_channel = discord.Object(id=target_channel_id)
#    print(str(target_channel))
    return target_channel, msg


async def say_message(message):
    target_channel, msg = say_mic_message(message)
    if target_channel != "" and msg != "":
        await client.send_message(target_channel, msg)
        
    # if message.attachments != None:
        # path = message.attachments[0]["url"]
        # await client.send_file(message.channel, path)
