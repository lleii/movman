#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
功能列表：
1.文件名解析：PTN集成
2.文件解析：MediaCoder集成
3.在线信息抓取：IMDB、DOUBAN

TODOLIST v2：
1.文件解析：MediaCoder集成
2.xls通过文件名点击播放；
3.imdb信息获取，ID来源：1英文名获取；2.豆瓣获取


BUG:
1.需要登录查询，否则404，如https://movie.douban.com/subject/5912992/


chrome cookie：~/Library/Application Support/Google/Chrome/Default/Cookies 

def StringRegexReplace(pattern,repl,string):  
    return  re.sub(pattern, repl, string, count=1, flags=re.I)  

def check_contain_chinese(check_str):
     for ch in check_str.decode('utf-8'):
         if u'\u4e00' <= ch <= u'\u9fff':
             return True
     return False

def isset(v): 
    try: 
        type (eval(v)) 
    except: 
        pprint (1)
        return 0 
    else: 
        pprint (2)
        return 1
'''

import string
import re
import requests
import json,time,csv
from pprint import pprint
import ptn
import os, sys
import pandas as pd
from mi import MediaInfo
import os.path

def init(cfg) :
    cfg['mode'] = ''
    cfg['dir'] = ["/Volumes/data/pt","/Volumes/data/old","/Volumes/data/tv"]

#删除文件，已观看
def is_done(f,aa) :
    if f["filename"] not in aa:
        f['status'] = "done"
        print(f["filename"])
        return 1        

    return 0
        

def main() :
    r = list() #index list
    f = dict() #row dict
    g = dict()
    a = list()
    aa = list()
    rb = list()
    cfg = dict() #config
    global search_rst,j

    init(cfg)
    
    o = pd.read_excel("o2.xlsx")
    b = o["filename"].tolist()

    for src_dir in cfg['dir']:
        a += os.listdir(src_dir)
    cfg['dir'] = ["","/Volumes/data/old","/Volumes/data/tv"]
    pt = os.listdir('/Volumes/data/pt')
    tv = os.listdir('/Volumes/data/tv')
    old = os.listdir('/Volumes/data/old')
    for index, row in o.iterrows():  
        f = row.to_dict()
        '''
        if f['filename'] in pt:
            f['dirpath'] = '/Volumes/data/pt'
            f['filepath'] = os.path.join(f['dirpath'], f['filename'])
            print(f['filepath'])
        if f['filename'] in tv:
            f['dirpath'] = '/Volumes/data/tv'
            f['filepath'] = os.path.join(f['dirpath'], f['filename'])
            print(f['filepath'])
        if f['filename'] in old:
            f['dirpath'] = '/Volumes/data/old'
            f['filepath'] = os.path.join(f['dirpath'], f['filename'])
            print(f['filepath'])
            f['mi_extname']=''
            f['mi_bitrate']=''
            f['mi_container']=''
            f['mi_duration']=''
            f['mi_fileSize']=''
        '''
        pprint (f['filepath'])
        if f['filepath'] != f['filepath'] or f['filepath'] is None:
            r.append(f)
            continue 
        if 'mi_duration' in f:
            if f['mi_duration'] == f['mi_duration'] and f['mi_duration'] != 0:
                r.append(f)
                continue


        if os.path.isdir(f['filepath']):
            f['mi_duration'] = 0
            f['mi_fileSize'] = 0
            for dirpath, dirnames, filenames in os.walk(f['filepath']):
                for filename in filenames:                    
                    if f['mi_extname'] in  ['.mkv','.mp4','.avi','.iso','.rmvb'] :
                        f['mi_extname'] = os.path.splitext(filename)[1].lower()
                        filepath = os.path.join(dirpath, filename)
                        #if os.path.getsize(filepath) > 1024*1024*100:
                        if 1:
                            print("file:" + filepath)
                            #a = os.path.splitext(filename)[1].lower()
                            info = MediaInfo (filename = filepath,cmd ='/usr/local/bin/mediainfo')
                            infoData = info.getInfo()

                            if infoData:
                            
                                if 'bitrate' in infoData:  
                                    f['mi_bitrate'] = int(infoData['bitrate'])//1000#Kbps
                                if 'container' in infoData:
                                    f['mi_container'] = infoData['container']
                                if 'duration' in infoData:
                                    f['mi_duration'] += int(infoData['duration'])//1000//60 #min
                                if 'fileSize' in infoData:
                                    f['mi_fileSize'] += int(infoData['fileSize'])//1024//1024 #MB
                                

                    
                #print (b)
        else:
            info = MediaInfo (filename = f['filepath'],cmd ='/usr/local/bin/mediainfo')
            infoData = info.getInfo()
            f['mi_extname'] = os.path.splitext(f['filename'])[1].lower()
            if infoData:
                if 'bitrate' in infoData:  
                    f['mi_bitrate'] = int(infoData['bitrate'])//1000
                if 'container' in infoData:
                    f['mi_container'] = infoData['container']
                if 'duration' in infoData:
                    f['mi_duration'] = int(infoData['duration'])//1000//60
                if 'fileSize' in infoData:
                    f['mi_fileSize'] = int(infoData['fileSize'])//1024//1024

        pprint (f['mi_duration'])
        r.append(f)




        df = pd.DataFrame(r) 
        #列排序    
        col=['is_fetch','id','status','filename','db_rating','db_ratings_count','mi_bitrate','mi_duration','mi_fileSize','filepath','dirpath','mi_extname','mi_container','title','db_title','db_directors','db_casts','db_countries','db_genres', 'db_subtype','db_year',  'db_summary', 'db_aka', 'db_alt', 'db_collect_count', 'db_comments_count', 'db_current_season',  'db_do_count', 'db_douban_site','db_episodes_count', 'db_id', 'db_images', 'db_mobile_url','db_original_title', 'db_reviews_count', 'db_schedule_url', 'db_seasons_count','db_share_url', 'db_stars',  'db_wish_count', 'durations', 'excess',  'group', 'languages', 'mainland_pubdate', 'photos','popular_reviews', 'pubdates', 'quality', 'resolution', 'search_url','season',  'url', 'website', 'writers','audio', 'codec', 'year','container']
        df = df[col]
        #行排序，by豆瓣评分
        df = df.sort_values(['db_rating'],ascending=0)
        df.to_excel("o6.xlsx")  



    return

    #新增文件，新下载
    for ai in a:
        if re.search("^\.", ai) or re.match("inc", ai):
            #pprint(ai)  
            continue
        if ai not in b:
            pprint(ai) 
            g = {}            
            g['filename'] = ai
            g['status'] = "new"
            rb.append(g)
        aa.append(ai)
    dfb = pd.DataFrame(rb,index= range(len(o),len(o)+len(rb))) 
    o=o.append(dfb)

    for index, row in o.iterrows():  

        #已抓取，跳过
        if cfg['mode'] != 'all' and row["is_fetch"] > 0 :
            f = row.to_dict()
            is_done (f,aa)
            r.append(f)
            continue

        print(index)#保留
        print(row["filename"])#保留

        #手工矫正ID
        if row["id"] is not None and row['status'] != "new":
            f = row.to_dict()
        else : #搜索获取ID
            i=row["filename"]

            f = ptn.PTN().parse(i)
            f["filename"] = i
            if row['status'] == "new":
                f["status"] = "new"

            f["search_url"] = "http://api.douban.com/v2/movie/search?q=" + f["title"].replace(' ','%20')
            search_rst = requests.get(f["search_url"]).json()

            if 'total' in search_rst and search_rst["total"] > 0 :
                f["id"] = search_rst["subjects"][0]["id"]

        #抓取信息
        if 'id' in f and f["id"] is not None:            
            pprint ("fetch")
            pprint (f["filename"])
            sid = f["id"]
            if f["id"] == f["id"] :#not NaN
                sid = int(f["id"])
            f["url"] = "http://api.douban.com/v2/movie/subject/" + str(sid)
            j = requests.get(f["url"]).json()

            n=0

            if 'rating' in j: 
                f["db_rating"] = j["rating"]["average"]
                f["db_stars"] = j["rating"]["stars"]
                n += 1

            if 'alt' in j: 
                f["db_alt"] = j["alt"]
                n += 1

            if 'aka' in j:  
                f["db_aka"] = j["aka"]
                n += 1

            if 'directors' in j: 
                n += 1
                f["db_directors"] = ""
                for x in j["directors"] :
                    f["db_directors"] += x["name"] + ";"

            if 'casts' in j: 
                n += 1
                f["db_casts"] = ""
                for x in j["casts"] :
                    f["db_casts"] += x["name"] + ";"

            if 'countries' in j: 
                f["db_countries"] = j["countries"]
                n += 1
            if 'genres' in j: 
                f["db_genres"] = j["genres"] 
                n += 1
            if 'summary' in j: 
                f["db_summary"] = j["summary"]
                n += 1
            if 'collect_count' in j: 
                f["db_collect_count"] = j["collect_count"]
                n += 1

            if 'comments_count' in j: 
                f["db_comments_count"] = j["comments_count"]
                n += 1

            if 'current_season' in j: 
                f["db_current_season"] = j["current_season"]
                n += 1

            if 'do_count' in j: 
                f["db_do_count"] = j["do_count"]
                n += 1

            if 'douban_site' in j: 
                f["db_douban_site"] = j["douban_site"]
                n += 1
            if 'episodes_count' in j: 
                f["db_episodes_count"] = j["episodes_count"]
                n += 1
            if 'id' in j: 
                f["db_id"] = j["id"]
                n += 1
            if 'images' in j: 
                f["db_images"] = j["images"]["small"]
                n += 1
            if 'mobile_url' in j: 
                f["db_mobile_url"] = j["mobile_url"]
                n += 1
            if 'original_title' in j: 
                f["db_original_title"] = j["original_title"]
                n += 1
            if 'ratings_count' in j: 
                f["db_ratings_count"] = j["ratings_count"]
                n += 1
            if 'reviews_count' in j: 
                f["db_reviews_count"] = j["reviews_count"]
                n += 1
            if 'schedule_url' in j: 
                f["db_schedule_url"] = j["schedule_url"]
                n += 1
            if 'seasons_count' in j: 
                f["db_seasons_count"] = j["seasons_count"]
                n += 1
            if 'share_url' in j: 
                f["db_share_url"] = j["share_url"]
                n += 1
            if 'subtype' in j: 
                f["db_subtype"] = j["subtype"]
                n += 1
            if 'title' in j: 
                f["db_title"] = j["title"]
                n += 1
            if 'wish_count' in j: 
                f["db_wish_count"] = j["wish_count"]
                n += 1
            if 'year' in j: 
                f["db_year"] = j["year"]
                n += 1
            if 'writers' in j: 
                f["db_writers"] = j["writers"]
                n += 1
            if 'website' in j: 
                f["db_website"] = j["website"]
                n += 1
            if 'pubdates' in j: 
                f["db_pubdates"] = j["pubdates"]
                n += 1
            if 'mainland_pubdate' in j: 
                f["db_mainland_pubdate"] = j["mainland_pubdate"]
                n += 1
            if 'languages' in j: 
                f["db_languages"] = j["languages"]
                n += 1
            if 'durations' in j: 
                f["db_durations"] = j["durations"]
                n += 1
            if 'photos' in j: 
                f["db_photos"] = j["photos"]
                n += 1
            if 'popular_reviews' in j: 
                f["db_popular_reviews"] = j["popular_reviews"]
                n += 1
            if n>0: #已抓取
                f["is_fetch"] = 1

        is_done(f,aa)#已观看
        r.append(f)
        time.sleep(1)#豆瓣:150次IO/min

    df = pd.DataFrame(r) 
    #列排序    
    col=['is_fetch','id','status','filename','title','db_title','db_rating','db_ratings_count','db_directors','db_casts','db_countries','db_genres', 'db_subtype','db_year',  'db_summary', 'db_aka', 'db_alt', 'db_collect_count', 'db_comments_count', 'db_current_season',  'db_do_count', 'db_douban_site','db_episodes_count', 'db_id', 'db_images', 'db_mobile_url','db_original_title', 'db_reviews_count', 'db_schedule_url', 'db_seasons_count','db_share_url', 'db_stars',  'db_wish_count', 'durations', 'excess',  'group', 'languages', 'mainland_pubdate', 'photos','popular_reviews', 'pubdates', 'quality', 'resolution', 'search_url','season',  'url', 'website', 'writers','audio', 'codec', 'year','container']
    df = df[col]
    #行排序，by豆瓣评分
    df = df.sort_values(['db_rating'],ascending=0)
    df.to_excel("o.xlsx")   

if __name__ == '__main__':
    main()









