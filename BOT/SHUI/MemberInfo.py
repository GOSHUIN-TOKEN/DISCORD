#coding: utf-8
# ver 2.1
import builtins

import re
import random
import requests
import json
import types
import base64
import os
import sys, datetime, time
import discord



def make_empty_member_info(message):
    memberinfo = {
        "eth_address": "",
        "waves_address": "",
        "omikuji_count": 0,
        "kaiwa_experiment": 0,
        "kaiwa_experiment_coef": 1,
        "user_id": message.author.id
    }
    
    return memberinfo
    