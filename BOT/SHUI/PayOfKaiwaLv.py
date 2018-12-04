import unicodedata
import builtins

import re
import json
import os
import sys, datetime, time
import traceback


LV_GET_COIN_TABLE = [
    [5,5000,],
    [10,17000,],
    [15,28000,],
    [20,51000,],
    [25,83000,],
    [30,124000,],
    [35,176000,],
    [40,240000,],
    [45,318000,],
    [50,409000,],
    [55,516000,],
    [60,640000,],
    [65,782000,],
    [70,942000,],
    [75,1122000],
    [80,1324000],
    [85,1548000],
    [90,1795000],
    [95,2066000],
    [100,2500000]
]

# そのレベルになるのに必要な総経験値(Mee6と同じ計算式)
def need_experiment_value(level):
    xp_to_desired_level = 5 / 6 * level * (2 * level * level + 27 * level + 91);
    return xp_to_desired_level


LV_TO_EXP_LIST = []
def createChatLevelUpTable():
    if len(LV_TO_EXP_LIST) ==0:
        # lv200まで埋める
        for lv in range(0, 201):
            LV_TO_EXP_LIST.append([lv, need_experiment_value(lv)])

    # print(LV_TO_EXP_LIST)



def get_lv_from_exp(exp):
    lv = 0
    for t in LV_TO_EXP_LIST:
        # 指定された経験値より、レベル表の総合経験値が低いなら
        if t[1] < exp:
            lv = t[0] # すくなくともそのレベルには到達している
    
    return lv

def get_coin_amount_from_lv(lv):
    amount = 0
    for t in LV_GET_COIN_TABLE:
        # 指定されたレベル以下は全部
        if t[0] <= lv:
            amount = amount + t[1] 
    
    return amount



def show_level_infomation(id, exp):

    try:
        lv = get_lv_from_exp(exp)
    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
        print("show_level_infomation 中エラー")


def CalclatePaid(YEAR_MONTH):

    postjsonfiles = os.listdir('DataMemberPostInfo')
    for path in postjsonfiles:
        try:
            exp = 0
            lv = 0
            id = 0
            amount = 0
            with open("DataMemberPostInfo/" + path, "r") as fr:
                postinfo = json.load(fr)
                id = postinfo["id"]
                exp = postinfo["exp"]
                lv = get_lv_from_exp(exp)
                amount = get_coin_amount_from_lv(lv)

            if os.path.exists("DataMemberPaid/" + str(id) + ".json"):
                paidinfo = None
                with open("DataMemberPaid/" + str(id) + ".json", "r") as fr2:
                    paidinfo = json.load(fr2)
                    if paidinfo["kaiwa_paid_lv"] == 0:
                        paidinfo["kaiwa_paid_lv"] = {}
                        paidinfo["kaiwa_paid_lv"][YEAR_MONTH] = lv
                    else:
                        paidinfo["kaiwa_paid_lv"][YEAR_MONTH] = lv

                    if not "kaiwa_paid_exp" in paidinfo:
                        paidinfo["kaiwa_paid_exp"] = {}
                        paidinfo["kaiwa_paid_exp"][YEAR_MONTH] = exp
                    else:
                        paidinfo["kaiwa_paid_exp"][YEAR_MONTH] = exp

                    if paidinfo["kaiwa_paid_amount"] == 0:
                        paidinfo["kaiwa_paid_amount"] = {}
                        paidinfo["kaiwa_paid_amount"][YEAR_MONTH] = amount
                    else:
                        paidinfo["kaiwa_paid_amount"][YEAR_MONTH] = amount

                if paidinfo:
                    with open("DataMemberPaid/" + str(id) + ".json", "w") as fw:
                        json_data = json.dumps(paidinfo, indent=4)
                        fw.write(json_data)

                #print("id:" + id)
                #print("lv:" + str(lv))
                #print("exp:" + str(exp))
        except Exception as e:
            t, v, tb = sys.exc_info()
            print(traceback.format_exception(t,v,tb))
            print(traceback.format_tb(e.__traceback__))
            print("ファイルオープン 中エラー")


createChatLevelUpTable()
CalclatePaid("201810")