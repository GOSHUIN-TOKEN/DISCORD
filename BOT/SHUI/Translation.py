# -*- coding: utf-8 -*-

# Copyright (C) 2018 Akitsugu Komiyama
# under the GPL v3 License.
#

import os
import json
import urllib.request

def get_gas_api_key() -> str:
    # 本番用のみが有効なら本番用の接続トークンを返す
    return os.getenv("GOOGLE_SCRIPT_TRANSLATION_API", r'')

# 少し遅いが長さ制限がほぼない
def TranslationMethodPost(text: str, src_lang: str, dst_lang: str) -> str:
    headers: str = {"Content-Type": "application/json"}

    script_url: str = r"https://script.google.com/macros/s/" + get_gas_api_key() + "/exec"

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
        response_json:dict = json.loads(response_body)
        return response_json["result"]

    return ""


# 少し早いがエンコードされた状態でURL含めて2000文字ほどという制限がある。
def TranslationMethodGet(text: str, src_lang: str, dst_lang: str) -> str:
    text = urllib.parse.quote(text)

    script_url: str = r"https://script.google.com/macros/s/" + get_gas_api_key() + "/exec"

    request_script_url = "{script_url}?text={text}&source={source}&target={target}".format(script_url=script_url,text=text,source=src_lang,target=dst_lang)

    req = urllib.request.Request(request_script_url)
    with urllib.request.urlopen(req) as res:
        byte_result = res.read()
        answer = byte_result.decode(encoding='utf-8')
        return answer

    return ""


if __name__ == "__main__":
    result = TranslationMethodPost("りんご", "ja", "en")
    print(result)
    #result = TranslationMethodGet("りんご", "ja", "en")
    #print(result)
