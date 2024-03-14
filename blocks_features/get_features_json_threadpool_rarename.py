# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 11:23:00 2023

@author: Killlua
"""

import numpy as np
import pandas as pd
import os
import gc
import re
import time

import Levenshtein

import jieba.analyse
from jieba.analyse import extract_tags
from ast import literal_eval
from concurrent.futures import ThreadPoolExecutor


def show_files(path, all_files):
    file_list = os.listdir(path)
    for file in file_list:
        cur_path = os.path.join(path, file)
        if os.path.isdir(cur_path):
            show_files(cur_path, all_files)
        else:
            all_files.append(cur_path)
    return all_files

def show_folders(path):
    all_folders = []
    for home, folders, files in os.walk(path):
        for dir in folders:
            cur_path = os.path.join(home, dir)
            file_list = show_folders(cur_path)
            if file_list:
                show_folders(cur_path)
            else:
                all_folders.append(os.path.join(home, dir))
    return all_folders

def replace_special_chars(string):
    # 定义正则表达式，匹配不能用于文件名的特殊字符
    pattern = r'[\\/:*?"<>|,]'
    # 将特殊字符替换为下划线
    return re.sub(pattern, '_', string)

# list intersection
def lst_intersec(a,b):
    if (a != None) and (b != None):
        if (len(a) != 0) and (len(b) != 0):
            return len(set(a).intersection(set(b)))
        else:
            return 0
    else:
        return 0

def lst_per(a,b):
    try:
        value = a/b
    except:
        value = 0
    return value

# values exist
def zeroifs(x,y):
    if (x != None) and (y != None):
        if (len(x) != 0) and (len(y) != 0):
            return 1
        else:
            return 0
    else:
        return 0

# strings' similarity
def match_name_lr(name1,name2):
    if (name1 != None) and (name2 != None):
        d = Levenshtein.ratio(name1,name2)
        if (name1 != '') and (name2 != ''):
            return d*100
        else:
            return 0
    else:
        return 0

# Checking each level of geographic similarity 
def calculate_geo_score(i, j, country, province, city, district, road, latitude, longitude):
    if (country[i] != country[j]) or any([country[i]=='',country[j]=='']):
        geo = 0
    if (country[i] == country[j]) and all([country[i] != '', country[j] != '']) and ((province[i] != province[j]) or any([province[i]=='',province[j]==''])):
        geo = 1
    if (country[i] == country[j]) and all([province[i] != '', province[j] != '']) and (province[i] == province[j]) and ((city[i] != city[j]) or any([city[i]=='',city[j]==''])):
        geo = 2
    if (province[i] == province[j]) and all([city[i] != '', city[j] != '']) and (city[i] == city[j]) and ((district[i] != district[j]) or any([district[i]=='',district[j]==''])):
        geo = 3
    if (country[i] == country[j]) and (province[i] == province[j]) and (city[i] == city[j]) and (district[i] != '') and (district[j] != '') and (district[i] == district[j]) and ((road[i] != road[j]) or any([road[i]=='',road[j]==''])):
        geo = 4
    if (country[i] == country[j]) and (province[i] == province[j]) and (city[i] == city[j]) and (district[i] == district[j]) and (road[i] != '') and (road[j] != '')  and (road[i] == road[j]):
        geo = 5
    if (latitude[i] != '') and (longitude[i] != '') and (latitude[j] != '') and (longitude[j] != '') and (latitude[i] == latitude[j]) and (longitude[i] == longitude[j]):
        geo = 6
    return geo

# geo exists
def geo_exist(i, j, geo, country, province, city, district, road, latitude, longitude):
    if geo == 0:
        if (country[i] != '') and (country[j] != ''):
            geo_est = 1
        else:
            geo_est = 0
    elif geo == 1:
        if (province[i] != '') and (province[j] != ''):
            geo_est = 1
        else:
            geo_est = 0
    elif geo == 2:
        if (city[i] != '') and (city[j] != ''):
            geo_est = 1
        else:
            geo_est = 0
    elif geo == 3:
        if (district[i] != '') and (district[j] != ''):
            geo_est = 1
        else:
            geo_est = 0
    elif geo == 4:
        if (road[i] != '') and (road[j] != ''):
            geo_est = 1
        else:
            geo_est = 0
    elif geo == 5:
        if (latitude[i] != '') and (longitude[i] != '') and (latitude[j] != '') and (longitude[j] != ''):
            geo_est = 1
        else:
            geo_est = 0
    else:
        geo_est = 1
    return geo_est

# citing/cited relationship
def citing_relationship(i, j, citing_lst, cited_lst, ida):
    if citing_lst[j] and (ida[i] in citing_lst[j]):
        return 1
    elif cited_lst[j] and (ida[i] in cited_lst[j]):
        return 1
    elif citing_lst[i] and (ida[j] in citing_lst[i]):
        return 1
    elif cited_lst[i] and (ida[j] in cited_lst[i]):
        return 1
    else:
        return 0

# citing/cited relationship exists
def citing_rp_est(i, j, citing_lst, cited_lst):
    if citing_lst[i] != None and cited_lst[i] != None and citing_lst[j] != None and cited_lst[j] != None:
        citing_lst_est = 1
        cited_lst_est = 1
    elif (citing_lst[i] == None and cited_lst[i] != None) or (citing_lst[j] == None and cited_lst[j] != None):
        citing_lst_est = 0
        cited_lst_est = 1
    elif (citing_lst[i] != None and cited_lst[i] == None) or (citing_lst[j] != None and cited_lst[j] == None):
        citing_lst_est = 1
        cited_lst_est = 0
    else:
        citing_lst_est = 0
        cited_lst_est = 0
    return [citing_lst_est, cited_lst_est]

def process_file(file):
    try:
        with open(file, 'r', encoding="utf-8") as f:
            content = f.readlines()
        block_name = os.path.splitext(os.path.basename(file))[0]
        block_values = [p.strip() for p in content]
        return block_name, block_values
    except Exception as e:
        print(f"Error reading {file}: {e}")
        return block_name, []

def output_file(file, features_data):
    with open(file, 'w', encoding="utf-8") as f:
        for i in features_data[os.path.basename(file).replace('.txt','')]:
            f.write(f'{i}\n')

def process_patents(scientist_folder, cnp_pnr_ida_dict, key_lst):
    block_files = show_files(scientist_folder,[])
    start_input = time.time()
    patents_data = {}
    with ThreadPoolExecutor(max_workers=12) as executor:
        # 提交所有文件处理任务，并保留futures以保持顺序
        futures = [executor.submit(process_file, file) for file in block_files]
        for future in futures:
            try:
                # 尝试解包future的结果
                block_name, block_values = future.result()
                patents_data[block_name] = block_values
            except ValueError as e:
                print(f"Error unpacking future result: {e}")
    print(f'{scientist_folder} input costs {time.time() - start_input}s')

    start = time.time()
    features_data = {}
    for k in key_lst:
        features_data[k] = []

    if (len(patents_data['patent_title']) != 0) and (all(not s for s in patents_data['patent_title']) != True):
        for i in range(len(patents_data['patent_title'])):
            for j in range(i + 1, len(patents_data['patent_title'])):
                if i != j:
                    features_data['patents_cp'].append(f'{patents_data["ida"][i]}_{patents_data["ida"][j]}')
                    # app_i
                    app_i_value = lst_intersec(literal_eval(patents_data['applicants_lst'][i]),
                                               literal_eval(patents_data['applicants_lst'][j]))
                    features_data['app_i'].append(app_i_value)
                    features_data['app_i_est'].append(zeroifs(literal_eval(patents_data['applicants_lst'][i]),
                                                              literal_eval(patents_data['applicants_lst'][j])))
                    features_data['app_i_per'].append(
                        max(lst_per(app_i_value, len(literal_eval(patents_data['applicants_lst'][i]))),
                            lst_per(app_i_value, len(literal_eval(patents_data['applicants_lst'][j])))))
                    # app_s
                    features_data['app_s'].append(
                        match_name_lr(patents_data['app_first'][i], patents_data['app_first'][j]))
                    features_data['app_s_est'].append(
                        zeroifs(patents_data['app_first'][i], patents_data['app_first'][j]))
                    # inventor_i
                    inventor_i_value = lst_intersec(literal_eval(patents_data['inventor_lst'][i]), literal_eval(patents_data['inventor_lst'][j]))
                    # label
                    if patents_data['scientist_name'][i] == patents_data['scientist_name'][j]:
                        features_data['label'].append(1)
                    else:
                        features_data['label'].append(0)
                        inventor_i_value = inventor_i_value + 1
                    features_data['inventor_i'].append(inventor_i_value)
                    features_data['inventor_i_est'].append(zeroifs(literal_eval(patents_data['inventor_lst'][i]), literal_eval(patents_data['inventor_lst'][j])))
                    features_data['inventor_i_per'].append(max(lst_per(inventor_i_value, len(literal_eval(patents_data['inventor_lst'][i]))),
                                         lst_per(inventor_i_value, len(literal_eval(patents_data['inventor_lst'][j])))))
                    # ipc_c
                    ipc_c_value = lst_intersec(literal_eval(patents_data['ipc_class'][i]),
                                               literal_eval(patents_data['ipc_class'][j]))
                    features_data['ipc_c'].append(ipc_c_value)
                    features_data['ipc_c_est'].append(
                        zeroifs(literal_eval(patents_data['ipc_class'][i]), literal_eval(patents_data['ipc_class'][j])))
                    features_data['ipc_c_per'].append(
                        max(lst_per(ipc_c_value, len(literal_eval(patents_data['ipc_class'][i]))),
                            lst_per(ipc_c_value, len(literal_eval(patents_data['ipc_class'][j])))))

                    # ipc_g
                    ipc_g_value = lst_intersec(literal_eval(patents_data['ipc_group'][i]),
                                               literal_eval(patents_data['ipc_group'][j]))
                    features_data['ipc_g'].append(ipc_g_value)
                    features_data['ipc_g_est'].append(
                        zeroifs(literal_eval(patents_data['ipc_group'][i]), literal_eval(patents_data['ipc_group'][j])))
                    features_data['ipc_g_per'].append(
                        max(lst_per(ipc_g_value, len(literal_eval(patents_data['ipc_group'][i]))),
                            lst_per(ipc_g_value, len(literal_eval(patents_data['ipc_group'][j])))))

                    # title
                    features_data['title'].append(
                        match_name_lr(patents_data['patent_title'][i], patents_data['patent_title'][j]))
                    features_data['title_est'].append(
                        zeroifs(patents_data['patent_title'][i], patents_data['patent_title'][j]))
                    # keywords
                    keywords_i = extract_tags(patents_data['patent_title'][i], topK=2)
                    keywords_j = extract_tags(patents_data['patent_title'][j], topK=2)
                    for keywords in [keywords_i, keywords_j]:
                        if len(keywords) < 2:
                            keywords += [None] * (2 - len(keywords))
                    features_data['keyword1'].append(match_name_lr(keywords_i[0], keywords_j[0]))
                    features_data['keyword2'].append(match_name_lr(keywords_i[1], keywords_j[1]))
                    features_data['keyword1_est'].append(zeroifs(keywords_i[0], keywords_j[0]))
                    features_data['keyword2_est'].append(zeroifs(keywords_i[1], keywords_j[1]))
                    # geo
                    geo_value = calculate_geo_score(i, j, patents_data['country'], patents_data['province'],
                                                    patents_data['city'], patents_data['district'],
                                                    patents_data['road'], patents_data['latitude'],
                                                    patents_data['longitude'])
                    features_data['geo'].append(geo_value)
                    features_data['geo_est'].append(
                        geo_exist(i, j, geo_value, patents_data['country'], patents_data['province'],
                                  patents_data['city'], patents_data['district'], patents_data['road'],
                                  patents_data['latitude'], patents_data['longitude']))
                    # citing
                    features_data['citing_rp'].append(
                        citing_relationship(i, j, patents_data['citing_lst'], patents_data['cited_lst'],
                                            patents_data['ida']))
                    features_data['citing_lst_est'].append(
                        citing_rp_est(i, j, patents_data['citing_lst'], patents_data['cited_lst'])[0])
                    features_data['cited_lst_est'].append(
                        citing_rp_est(i, j, patents_data['citing_lst'], patents_data['cited_lst'])[1])
                    # diff_days
                    adate_i = np.datetime64(cnp_pnr_ida_dict.get(patents_data['ida'][i], '9999-12-31'))
                    adate_j = np.datetime64(cnp_pnr_ida_dict.get(patents_data['ida'][j], '9999-12-31'))
                    features_data['diff_days'].append(np.abs(adate_i - adate_j).astype('timedelta64[D]').astype(int))
                    # address_s
                    features_data['address_s'].append(
                        match_name_lr(patents_data['detailed_address'][i], patents_data['detailed_address'][j]))
                    features_data['address_s_est'].append(
                        zeroifs(patents_data['detailed_address'][i], patents_data['detailed_address'][j]))
    print(f'{scientist_folder} calculation costs {time.time() - start}s')

    start_output = time.time()
    file_path = scientist_folder.replace('blocks', 'features')
    os.makedirs(file_path, exist_ok=True)
    with ThreadPoolExecutor(max_workers=12) as t:
        for key in key_lst:
            t.submit(output_file, os.path.join(file_path,f'{key}.txt'),features_data)
    print(f'{file_path} output costs {time.time()-start_output}s')

jieba.load_userdict('raw_data/lexicon.txt')


key_lst = ['patents_cp', 'app_i', 'app_i_est', 'app_i_per', 'app_s', 'app_s_est',
               'inventor_i', 'inventor_i_est', 'inventor_i_per', 'ipc_c', 'ipc_c_est', 'ipc_c_per',
               'ipc_g', 'ipc_g_est', 'ipc_g_per', 'title', 'title_est',
               'keyword1', 'keyword1_est',
               'keyword2', 'keyword2_est',
               'address_s', 'address_s_est',
               'geo', 'geo_est',
               'citing_rp', 'citing_lst_est', 'cited_lst_est', 'diff_days', 'label']
if __name__ == "__main__":
    blocks_lst = show_folders('rarename_blocks')
    cnp_pnr_ida = pd.read_csv('../cnp_pnr_ida.csv')
    cnp_pnr_ida_dict = dict(zip(cnp_pnr_ida['ida'], cnp_pnr_ida['adate']))
    del cnp_pnr_ida
    gc.collect()

    with ThreadPoolExecutor(16) as t:
        for jf in blocks_lst:
            t.submit(process_patents, jf, cnp_pnr_ida_dict, key_lst)

    print('features_total_split finished.')




