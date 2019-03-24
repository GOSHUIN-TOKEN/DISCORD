
from __future__ import print_function
import os
import requests
from bs4 import BeautifulSoup
import csv
import time
import pprint
import copy
import asyncio

# 全ホルダーの枚数や順位、比率バランスを辞書で得る


CONTRACT_ADD = "0x06Ff3fD51eEd930878C15C65184Da5BfdD61FC69" # GSIN
HOLDERS_URL = "https://etherscan.io/token/generic-tokenholders2?a={}&s=0&p=".format(CONTRACT_ADD)

def getData(sess, page):
    url = HOLDERS_URL + page
    print("Retrieving page", page)
    return BeautifulSoup(sess.get(url).text, 'html.parser')

def getPage(sess, page):
    table = getData(sess, str(int(page))).find('table')
    return [[X.text.strip() for X in row.find_all('td')] for row in table.find_all('tr')]

# 外部が参照するデータ
externalHoldersRatioData = {}

# 今蓄積してる最中のデータ
internalHoldersRatioData = {}


async def ReCalculateHoldersRatio():
    global externalHoldersRatioData
    global internalHoldersRatioData

    resp = requests.get(HOLDERS_URL)
    sess = requests.Session()

    page = 0
    while True:
        page += 1
        data = getPage(sess, page)
        print(str(data))
        print(len(data))

        # 有効なデータが１つでもあるか
        data_exist = False
        for d in data:
            if len(d) < 4:
                continue
            internalHoldersRatioData[ d[1] ] = [ d[0], d[2], d[3] ]

            # 有効なデータがあった
            data_exist = True

        # 有効なデータが１つもないのであれば、それ以降みても無駄である。
        if not data_exist:
            break

        # あまり連続でアクセスしすぎるとSPAM認定されかねないので、間隔をあける
        await asyncio.sleep(2)

    # 外部が参照するデータへと書き込み。
    # 時間をかけてデータを蓄積しているため、このようにすべてを蓄積しおえた
    # タイミングで上書きする。
    externalHoldersRatioData = copy.deepcopy(internalHoldersRatioData)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(ReCalculateHoldersRatio())
    print(results)
    pprint.pprint(externalHoldersRatioData)
