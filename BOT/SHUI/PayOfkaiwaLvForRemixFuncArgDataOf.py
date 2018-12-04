import re
import json
import os
import sys, datetime, time
import traceback



def CalclateERCPaid(YEAR_MONTH):


    print_ethadd = []
    print_amount = []

    memberinfo = {}
    memberfiles = os.listdir('DataMemberInfo')
    for path in memberfiles:
        try:
            with open("DataMemberInfo/" + path, "r") as fr:
                postinfo = json.load(fr)
                id = postinfo["user_id"]
                eth = postinfo["eth_address"]
                memberinfo[id] = eth

                with open("DataMemberPaid/" + str(id) + ".json", "r") as fr2:
                    paidinfo = json.load(fr2)
                    if paidinfo["kaiwa_paid_amount"] != 0:
                        amount = paidinfo["kaiwa_paid_amount"][YEAR_MONTH]
                        if "201809" in paidinfo["kaiwa_paid_amount"]:
                            amount = amount - paidinfo["kaiwa_paid_amount"]["201809"]

                        if amount > 0:
                            print_ethadd.append(eth)
                            print_amount.append(amount)
        except Exception as e:
            t, v, tb = sys.exc_info()
            print(traceback.format_exception(t,v,tb))
            print(traceback.format_tb(e.__traceback__))
            print("ファイルオープン 中エラー")

    print("len(eth):" + str(len(print_ethadd)))
    print("len(amo):" + str(len(print_amount)))

    collected_count = 17
        
    report = ""
    pre_ix = 0
    while(True):
        ix = pre_ix + collected_count
        report += str(print_ethadd[pre_ix:ix]) + "\n"
        report += str(print_amount[pre_ix:ix]) + "\n"
        report += "\n"
        pre_ix = ix
        if ix > len(print_ethadd):
            break


    report = report.replace("'", '"')

    path = './PaymentReprtKaiwa' + YEAR_MONTH + '.txt'
    f = open(path, "w")
    f.write(report)
    f.close()


CalclateERCPaid("201810")