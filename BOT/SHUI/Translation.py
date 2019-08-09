# -*- coding: utf-8 -*-

# Copyright (C) 2018 Akitsugu Komiyama
# under the GPL v3 License.
#

import os
import json
import urllib.request
import discord
import re
import sys
import traceback

def get_gas_api_key() -> str:
    # 本番用のみが有効なら本番用の接続トークンを返す
    return os.getenv("GOOGLE_SCRIPT_TRANSLATION_API", r'')

# 少し遅いが長さ制限がほぼない
def translation_method_post(text: str, src_lang: str, dst_lang: str) -> str:
    try:
        headers: str = {"Content-Type": "application/json"}

        script_url: str = get_gas_api_key()

        data: dict  = {
            "text": text,
            "source": src_lang,
            "target": dst_lang
        }
        json_data: str = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(script_url, json_data, method="POST", headers=headers)
        with urllib.request.urlopen(req) as res:
            byte_result = res.read()
            response_body: str = byte_result.decode(encoding='utf-8')
            print(response_body)
            response_json: dict = json.loads(response_body)
            return response_json["result"]

        return ""

    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        return "Translate Error!!"


def is_translation_condition(message: discord.Message) -> bool:
    msg = str(message.content).strip()
    if re.match(r"^!translate\s+(.+)\s+(.+)", msg):
        return True

    return False

async def translate(message: discord.Message) -> str:
    msg = str(message.content).strip()
    ma = re.search(r"^!translate\s+(.{2,5}?)\s+(.+)$", msg, re.MULTILINE | re.DOTALL )
    if ma:
        dst_lang = ma.group(1)
        print(dst_lang)
        text = ma.group(2)
        print(text)
        trans_text = translation_method_post(text, "", dst_lang)
        return trans_text



if __name__ == "__main__":
    result = translation_method_post("りんご", "ja", "en")
    print(result)
