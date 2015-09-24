import os
import PIL
import time
import string
from multiprocessing import Pool
from PIL import Image
from readDataParallel import *
import numpy as np
import scipy as sp 
import matplotlib.pyplot as plt
import matplotlib as mpl
THEAD_NUM=16#进程数
SEPARATOR_1=' '     #空格分隔符
SEPARATOR_2=','     #以‘，’为分隔符
SEPARATOR_3=';'     #以‘;’为分隔符
MATCH_SET_FILENAME='dim_fashion_match_sets.txt' #穿衣搭配套餐
ITEMS_FILENAME='dim_items.txt'  #商品信息表：dim_items
USER_BUY_HISTORY='user_bought_history.txt'  #用户历史行为表：user_bought_history
TEST_READ='test.txt'
SPLIT_FOLD_NAME='SPLIT'
SPLIT_NUM=1000

### 读取达人推荐搭配
def readMatchSet(filename):
    print '*************readMatchSet*****************'
    time1=time.time()
    fp_match_set=open(filename,'r')
    MatchSet={}
    countLine=0     
    for line in fp_match_set.readlines():                   
        countLine=countLine+1
        coll_id,item_list=line.split(SEPARATOR_1)   #以空格作为分割符号
        detail_item=item_list.split(SEPARATOR_3)    #以‘;’为分隔符
        detain_item_list=[]
        for item_1 in detail_item:
            item_2= item_1.split(SEPARATOR_2)     #以‘，’为分隔符
            item_2_list=[]
            for item in item_2:     
                item_2_list.append(string.atoi(item))     #转化为整形
            detain_item_list.append(item_2_list) 
        MatchSet[string.atoi(coll_id)]=detain_item_list
    fp_match_set.close()
    time2=time.time()    
    print 'cost time: '+str(time2-time1)+' s'
    print '************************************************'
    return MatchSet

##删除列表中所有item条目
def removeAllSame(L,item):
    M=[]
    for i in range(0,len(L)):
        if(L[i]!=item):
            M+=[L[i]]
    return M       
###计算两个list之间的相似度
def similarFactor(List1,List2):
    return len(set(List1).intersection(set(List2)))*2.0/(len(set(List1))+len(set(List2)))
### 读取所有的商品信息
def readItems(filename):
    print '****************readItems*************'
    time1=time.time()
    fp_items=open(filename,'r')
    Items={}
    CategoryItem={} #以类目ID作为key
    keyWords={}  #用来存储各个商品分词所对应的商品
    countLine=0
    for line in fp_items.readlines():
        countLine=countLine+1
        item_id,cat_id,terms=line.split(SEPARATOR_1) #以空格作为分割符号
        item_id=string.atoi(item_id)
        cat_id=string.atoi(cat_id)   
        if(keyWords.has_key(cat_id)==False):
            keyWords[cat_id]={}
        
        item_info=[cat_id]
        terms_sp=terms.split(SEPARATOR_2)
        terms_list=[]
        for termStr in terms_sp:
            term=string.atoi(termStr)
            terms_list.append(term)
            if keyWords[cat_id].has_key(term)==False:
                keyWords[cat_id][term]=[item_id]
            else:
                keyWords[cat_id][term]+=[item_id]                        
        
        if(CategoryItem.has_key(cat_id)==False):
            CategoryItem[cat_id]={}
            CategoryItem[cat_id][item_id]=terms_list
        else:
            CategoryItem[cat_id][item_id]=terms_list
        
        item_info+=terms_list      
        Items[item_id]=item_info
    fp_items.close()
    for cat_id in keyWords.keys():
        for key in keyWords[cat_id].keys():       
            keyWords[cat_id][key]=list(set(keyWords[cat_id][key]))
    
    lowFreTh=4  #设置要清理的低频关键词，如果小于该阈值将把该商品的该关键词删除
    for key1 in keyWords.keys():
        for key2 in keyWords[key1]:
            if(len(keyWords[key1][key2])<lowFreTh):
                for i in keyWords[key1][key2]:  
                    Items[i]=removeAllSame(Items[i],key2);
                    CategoryItem[key1][i]= removeAllSame(CategoryItem[key1][i],key2);
    
    time2=time.time()        
    print 'cost time: '+str(time2-time1)+' s'   
    return Items,CategoryItem,keyWords
   
#将大文件进行分割
def splitFile(filename,split_num):   
    print '*******************splite*************'
    time1=time.time()
    fo=open(filename,'r')
    lineNum=len(fo.readlines()) #读取总共的行数
    stepLen=lineNum/split_num
    print 'lineNum:'+str(lineNum)
    fo.close()
    fo=open(filename,'r')
    for i in range(0,lineNum):
        lineStr=fo.readline()
        if(i%stepLen==0):
            index=i/stepLen            
            if index>0:
                fw.writelines(str1)
                fw.close()
            newFile ='./SPLIT1/'+str(index)+'.txt'
            fw=open(newFile,'w')
            str1=[lineStr]
        else:
            str1+=[lineStr]
        if (i==lineNum-1):
            fw.writelines(str1)
            fw.close()
    fo.close()
    time2=time.time()
    print 'cost time:'+str(time2-time1)+' s'
    print '****************************************'

### 并行计算的方式读取用户的购买信息
def readUserHistory():
    print '*******************readUserHistory*************'
    time1=time.time()
    if os.path.exists('SPLIT')==False:#是否存在SPILT文件夹，如果不存在则创建
        os.mkdir('SPLIT')
        splitFile(USER_BUY_HISTORY,1000) #分成1000份
        
    pool=Pool(THEAD_NUM)
    results=pool.map(readUserBuyHistoryPara,get_txt_paths('SPLIT'))
    pool.close()
    pool.join()
    userBuy={} 
    minTime=99999999
    maxTime=0
    for index in range(0,len(results)):
        for  user_id in results[index].keys():
            if userBuy.has_key(user_id)==False:
                userBuy[user_id]=results[index][user_id]                
            else:
                userBuy[user_id]+=results[index][user_id]
            for j in range(0,len(results[index][user_id])):
                curTime=results[index][user_id][j][1]
                if(curTime>maxTime):
                    maxTime=curTime
                if(curTime<minTime):
                    minTime=curTime
            #确定最大时间和最小时间         
    time2=time.time()
    print 'cost time:'+str(time2-time1)+' s'
    print '****************************************'
    return userBuy,minTime,maxTime

#####使用基于Item-to-Item的算法来对给定的item_id进行求算与之相似的item_id
def calSimilarItem(Items,CategoryItem,keyWords,item_id):
    print '*******************calSimilarItem*************'
    time1=time.time()
    similarItems={} #字典，用来保存所有和item_id有关的item
    cat_id=Items[item_id][0]
    for term1 in Items[item_id][1:]:
        for item in keyWords[cat_id][term1]: #查找关键词表中，包含term1的所有商品ID
            if item!=item_id:   
                if similarItems.has_key(item)==False:#由于多个关键词会导致重复，这里去除重复
                    similarItems[item]=similarFactor(Items[item],Items[item_id])
    time2=time.time()
    print 'cost time:'+str(time2-time1)+' s'
    print '****************************************'
    return similarItems
                    
###根据达人体检搭配给出相似关系和搭配相关度
def calSimilarAndCorrPro(MatchSet):
    print '*******************calSimilarAndCorrPro*************'
    time1=time.time()
    similarPro={}
    corrPro={}
    #计算相似度
    for key in MatchSet.keys():
        for i in range(0,len(MatchSet[key])):
            if len(MatchSet[key][i])>1:
                for m in range(0,len(MatchSet[key][i])):
                    item1=MatchSet[key][i][m]
                    for n in range(m+1,len(MatchSet[key][i])):
                        item2=MatchSet[key][i][n]
                        #添加（item1，item2）到item1的元素中
                        if similarPro.has_key(item1)==False:
                            similarPro[item1]={}
                            similarPro[item1][item2]=1
                        else:
                            if similarPro[item1].has_key(item2)==False:
                                similarPro[item1][item2]=1
                            else:
                                similarPro[item1][item2]+=1
                        #添加（item2,item1）到item1的元素中
                        if similarPro.has_key(item2)==False:
                            similarPro[item2]={}
                            similarPro[item2][item1]=1
                        else:
                            if similarPro[item2].has_key(item1)==False:                                
                                similarPro[item2][item1]=1
                            else:
                                similarPro[item2][item1]+=1    
    #计算相关性
    for key in MatchSet.keys():
        for i in range(0,len(MatchSet[key])):
            cat1=MatchSet[key][i]
            for j in range(i+1,len(MatchSet[key])):
                cat2=MatchSet[key][j]
                for m in range(0,len(cat1)):
                    item1=cat1[m]
                    for n in range(0,len(cat2)):
                        item2=cat2[n]
                        ##添加(item1,item2)到item1的元素中
                        if corrPro.has_key(item1)==False:
                            corrPro[item1]={}
                            corrPro[item1][item2]=1
                        else:
                            if corrPro[item1].has_key(item2)==False:
                                corrPro[item1][item2]=1
                            else:
                                corrPro[item1][item2]+=1
                        ##添加（item2，item1）到item2的元素中
                        if corrPro.has_key(item2)==False:
                            corrPro[item2]={}
                            corrPro[item2][item1]=1
                        else:
                            if corrPro[item2].has_key(item1)==False:
                                corrPro[item2][item1]=1
                            else:
                                corrPro[item2][item1]+=1
    time2=time.time()
    print 'cost time:'+str(time2-time1)+' s'
    print '****************************************'    
    return similarPro,corrPro
                                
## 根据用户购买的历史记录，计算商品的相关性和相似性
def calSimilarAndCorrUser(UserBuy):
    
    
               
    
            

#### 读取原始数据      
MatchSet= readMatchSet(MATCH_SET_FILENAME) 
Items,CategoryItem,keyWords=readItems(ITEMS_FILENAME)
UserBuy,minTime,maxTime=readUserHistory()  #读取用户的信息 

### 计算相关度和相似度
#根据商品的关键词来计算商品间的相似性，这里暂时没有使用图片信息，这里返回指定item_id的所有相似商品id
item_id=596 
similarItems=calSimilarItem(Items,CategoryItem,keyWords,item_id)

## 根据达人推荐搭配计算相似性和相关性
similarPro,corrPro=calSimilarAndCorrPro(MatchSet)

## 根据用户购买的历史记录，计算商品的相关性和相似性




 
        
    
    
    
    
    
    
    
    
    
    