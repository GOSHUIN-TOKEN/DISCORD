# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Akitsugu Komiyama
# under the GPL v3 License.
# 

import os


def get_discord_bot_token():
    # 本番用のみが有効なら本番用の接続トークンを返す
    BOT_TOKEN = os.getenv("DISCORD_SHUI_TOKEN", r'')
    if BOT_TOKEN != "":
        return BOT_TOKEN

    print("エラー: 環境変数のDISCORD_SHUI_TOKENが設定されていない")
    return None



