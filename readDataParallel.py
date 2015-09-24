# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 02:09:29 2015

@author: lzhq28
"""
import os
import string
import PIL
from PIL import Image

SEPARATOR_1=' '     #空格分隔符
SEPARATOR_2=','     #以‘，’为分隔符
SEPARATOR_3=';'     #以‘;’为分隔符


def get_txt_paths(folder):
    return (os.path.join(folder, f)
       for f in os.listdir(folder)
            if 'txt' in f)

 
          
### 读取穿衣搭配套餐数据
def readUserBuyHistoryPara(filename):
    fo=open(filename,'r')
    UserBuy={}
    for line in fo.readlines():
        user_id,item_id,create_at=line.split(SEPARATOR_1)
        if(UserBuy.has_key(string.atoi(user_id))):
            UserBuy[string.atoi(user_id)].append([string.atoi(item_id),string.atoi(create_at)])
        else:
            UserBuy[string.atoi(user_id)]=[[string.atoi(item_id),string.atoi(create_at)]]
                   
    fo.close()
    return UserBuy



 
    
 