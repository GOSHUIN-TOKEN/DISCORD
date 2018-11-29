import requests
import sys
import re
import json

import builtins

def get_input_jpy(text):
    m = re.search("^(\d+)\s*(円|yen)?$", text, re.IGNORECASE)
    try:
        yen = m.group(1)
        return float(yen)
    except:
        return 0

def get_btc_jpy():
    try:
        res = requests.get('https://coincheck.com/api/rate/btc_jpy')
        res.raise_for_status()
        python_obj = json.loads(res.text)
        return float(python_obj["rate"])
    except:
        return 0


def get_bda_num(msg):
    btc_jpy = get_btc_jpy()
    input_jpy = get_input_jpy(msg)
    bda_sat = 0.000000005
    
    return input_jpy / (btc_jpy * bda_sat)

def is_permission_teamhousyu_condition(message):
    ch = str(message.channel)
    if ch in ["運営報酬計算君"]:
       return True

    return False

async def say_message(message):
    ret = get_bda_num(message.content)
    await client.send_message(message.channel, str(int(ret)) + "枚 BDA(ERC) くれくれ♪")


# テスト
if __name__ == '__main__':
    # btc_jpy = get_btc_jpy()
    # input_jpy = get_input_jpy("86500")
    
    ret = get_bda_num("86500円")
    print(ret)
    