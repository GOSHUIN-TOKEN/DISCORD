# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Akitsugu Komiyama
# under the GPL v3 License.
#

import unicodedata

# 該当テキストを等幅フォントに置き換えた際の幅を得る
def get_east_asian_width_count_touhaba(text: str) -> int:
    count = 0
    for c in text:
        if unicodedata.east_asian_width(c) in 'FWA':
            count += 2
        else:
            count += 1
    return count



# 該当テキストを入力労力に比較的沿う形のカウンター
def get_east_asian_width_count_effort(text: str) -> int:
    ch_len: int = 0
    try:
        ch_len = len(text.encode("utf-8"))
        return ch_len
    except:
        pass

    try:
        ch_len = len(text)
        return ch_len
    except:
        pass

    return 0


