# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 11:23:00 2023

@author: Killlua
"""

from tqdm import tqdm
import os
import json
import gc
import re

import Levenshtein

import jieba
import jieba.analyse
from concurrent.futures import ThreadPoolExecutor

# 遍历文件夹中所有文件，将文件路径传入list
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


# 姓名作为文件名，把不能放入文件名的字符替换为下划线
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

# values exist
def zeroifs(x,y):
    if (x != None) and (y != None):
        if (len(x) != 0) and (len(y) != 0):
            return 1
        else:
            return 0
    else:
        return 0

# 字符串相似度
def match_name_lr(name1,name2):
    if (name1 != None) and (name2 != None):
        d = Levenshtein.ratio(name1,name2)
        if (name1 != '') and (name2 != ''):
            return d*100
        else:
            return 0
    else:
        return 0

# 地理位置匹配度
def calculate_geo_score(patents, i, j):   
    if (patents[i]['country'] != patents[j]['country']) or ((patents[i]['country'] == '')and(patents[j]['country'] == '')):
        geo = 0
    if (patents[i]['country'] == patents[j]['country']) and (patents[i]['country'] != '') and (patents[j]['country'] != '') and ((patents[i]['province'] != patents[j]['province']) or ((patents[i]['province'] == '') and (patents[j]['province'] == ''))):
        geo = 1
    if (patents[i]['country'] == patents[j]['country']) and (patents[i]['province'] != '') and (patents[j]['province'] != '') and (patents[i]['province'] == patents[j]['province']) and ((patents[i]['city'] != patents[j]['city']) or ((patents[i]['city'] == '') and (patents[j]['city'] == ''))):
        geo = 2
    if (patents[i]['province'] == patents[j]['province']) and (patents[i]['city'] != '') and (patents[j]['city'] != '') and (patents[i]['city'] == patents[j]['city']) and ((patents[i]['district'] != patents[j]['district']) or ((patents[i]['district'] == '') and (patents[j]['district'] == ''))):
        geo = 3
    if (patents[i]['country'] == patents[j]['country']) and (patents[i]['province'] == patents[j]['province']) and (patents[i]['city'] == patents[j]['city']) and (patents[i]['district'] != '') and (patents[j]['district'] != '') and (patents[i]['district'] == patents[j]['district']) and ((patents[i]['road'] != patents[j]['road']) or ((patents[i]['road'] == '') and (patents[j]['road'] == ''))):
        geo = 4
    if (patents[i]['country'] == patents[j]['country']) and (patents[i]['province'] == patents[j]['province']) and (patents[i]['city'] == patents[j]['city']) and (patents[i]['district'] == patents[j]['district']) and (patents[i]['road'] != '') and (patents[j]['road'] != '')  and (patents[i]['road'] == patents[j]['road']):
        geo = 5
    if (patents[i]['latitude'] != '') and (patents[i]['longitude'] != '') and (patents[j]['latitude'] != '') and (patents[j]['longitude'] != '') and (patents[i]['latitude'] == patents[j]['latitude']) and (patents[i]['longitude'] == patents[j]['longitude']):
        geo = 6
    return geo

# 地理位置是否存在
def geo_exist(patents, i, j, geo):
    if geo == 0:
        if (patents[i]['country'] != '') and (patents[j]['country'] != ''):
            geo_est = 1
        else:
            geo_est = 0
    elif geo == 1:
        if (patents[i]['province'] != '') and (patents[j]['province'] != ''):
            geo_est = 1
        else:
            geo_est = 0
    elif geo == 2:
        if (patents[i]['city'] != '') and (patents[j]['city'] != ''):
            geo_est = 1
        else:
            geo_est = 0
    elif geo == 3:
        if (patents[i]['district'] != '') and (patents[j]['district'] != ''):
            geo_est = 1
        else:
            geo_est = 0
    elif geo == 4:
        if (patents[i]['road'] != '') and (patents[j]['road'] != ''):
            geo_est = 1
        else:
            geo_est = 0
    elif geo == 5:
        if (patents[i]['latitude'] != '') and (patents[i]['longitude'] != '') and (patents[j]['latitude'] != '') and (patents[j]['longitude'] != ''):
            geo_est = 1
        else:
            geo_est = 0
    else:
        geo_est = 1
    return geo_est

# 是否存在引用关系
def citing_relationship(patents, i, j):
    if patents[j]["citing_lst"] and (patents[i]["ida"] in patents[j]["citing_lst"]):
        return 1
    elif patents[j]["cited_lst"] and (patents[i]["ida"] in patents[j]["cited_lst"]):
        return 1
    elif patents[i]["citing_lst"] and (patents[j]["ida"] in patents[i]["citing_lst"]):
        return 1
    elif patents[i]["cited_lst"] and (patents[j]["ida"] in patents[i]["cited_lst"]):
        return 1
    else:
        return 0

# 有无引用关系的特征值
def citing_rp_est(patents, i, j):
    if patents[i]["citing_lst"] != None and patents[i]["cited_lst"] != None and patents[j]["citing_lst"] != None and patents[j]["cited_lst"] != None:
        citing_lst_est = 1
        cited_lst_est = 1
    elif (patents[i]["citing_lst"] == None and patents[i]["cited_lst"] != None) or (patents[j]["citing_lst"] == None and patents[j]["cited_lst"] != None):
        citing_lst_est = 0
        cited_lst_est = 1
    elif (patents[i]["citing_lst"] != None and patents[i]["cited_lst"] == None) or (patents[j]["citing_lst"] != None and patents[j]["cited_lst"] == None):
        citing_lst_est = 1
        cited_lst_est = 0
    else:
        citing_lst_est = 0
        cited_lst_est = 0
    return [citing_lst_est, cited_lst_est]

# 生成特征值
def process_patents(json_path):
    # 读取block文件
    with open(json_path, mode='r', encoding='utf-8') as file:
        block = json.load(file)
        inventor = list(block.keys())[0]
        patents = block[inventor]
    features_list = []           
    # app_i
    app_lst = [patent['applicants_lst'] for patent in patents]
    
    if app_lst:
        app_i = [[lst_intersec(a,b) for b in app_lst] for a in app_lst]
        app_i_est = [[zeroifs(a,b) for b in app_lst] for a in app_lst]
    else:
        app_i = [[0 for patentb in patents] for patenta in patents]
        app_i_est= [[0 for patentb in patents] for patenta in patents]
        
    # inventor_i
    co_inventor_lst = [patent['inventor_lst'] for patent in patents]
    
    if co_inventor_lst:
        co_inventor_i = [[lst_intersec(a,b) for b in co_inventor_lst] for a in co_inventor_lst]
        co_inventor_i_est = [[zeroifs(a,b) for b in co_inventor_lst] for a in co_inventor_lst]
    else:
        co_inventor_i = [[0 for patentb in patents] for patenta in patents]
        co_inventor_i_est= [[0 for patentb in patents] for patenta in patents]
        
    # ipc_c
    ipc_c_lst = [patent['ipc_class'] for patent in patents]
    
    if ipc_c_lst:
        ipc_c_i = [[lst_intersec(a,b) for b in ipc_c_lst] for a in ipc_c_lst]
        ipc_c_i_est = [[zeroifs(a,b) for b in ipc_c_lst] for a in ipc_c_lst]
    else:
        ipc_c_i = [[0 for patentb in patents] for patenta in patents]
        ipc_c_i_est= [[0 for patentb in patents] for patenta in patents]
        
    # ipc_g
    ipc_g_lst = [patent['ipc_group'] for patent in patents]
    
    if ipc_g_lst:
        ipc_g_i = [[lst_intersec(a,b) for b in ipc_g_lst] for a in ipc_g_lst]
        ipc_g_i_est = [[zeroifs(a,b) for b in ipc_g_lst] for a in ipc_g_lst]
    else:
        ipc_g_i = [[0 for patentb in patents] for patenta in patents]
        ipc_g_i_est= [[0 for patentb in patents] for patenta in patents]
        

    # app_s
    app_first_lst = [patent['app_first'] for patent in patents]
    
    if app_first_lst:
        app_first_s = [[match_name_lr(a, b) for b in app_first_lst] for a in app_first_lst]
        app_first_s_est = [[zeroifs(a,b) for b in app_first_lst] for a in app_first_lst]
    else:
        app_first_s = [[0 for patentb in patents] for patenta in patents]
        app_first_s_est = [[0 for patentb in patents] for patenta in patents]
        
    # address_s
    da_lst = [patent['detailed_address'] for patent in patents]
    
    if da_lst:
        da_s = [[match_name_lr(a, b) for b in da_lst] for a in da_lst]
        da_s_est = [[zeroifs(a,b) for b in da_lst] for a in da_lst]
    else:
        da_s = [[0 for patentb in patents] for patenta in patents]
        da_s_est = [[0 for patentb in patents] for patenta in patents]
        
    # title
    titles = [patent['patent_title'] for patent in patents]
    if (len(titles)!=0) and (all(not s for s in titles) != True):
        title = [[match_name_lr(t1, t2) for t2 in titles] for t1 in titles]
        title_est = [[zeroifs(t1,t2) for t2 in titles] for t1 in titles]
        # keyword similarity
        keywords = [jieba.analyse.extract_tags(patent['patent_title'],topK = 2) for patent in patents]
        # 为每对标题计算关键词相似度
        for i in tqdm(range(len(keywords)), desc='features processing', total=len(keywords)):
            for j in range(i + 1, len(keywords)):
                # 计算每一对标题的关键词相似度
                if patents[i]["ida"] != patents[j]["ida"]:
                    kw_sim_1 = match_name_lr(keywords[i][0], keywords[j][0]) if len(keywords[i]) > 0 and len(keywords[j]) > 0 else 0
                    kw_sim_2 = match_name_lr(keywords[i][1], keywords[j][1]) if len(keywords[i]) > 1 and len(keywords[j]) > 1 else 0
                    kw_sim_1_est = zeroifs(keywords[i][0], keywords[j][0]) if len(keywords[i]) > 0 and len(keywords[j]) > 0 else 0
                    kw_sim_2_est = zeroifs(keywords[i][1], keywords[j][1]) if len(keywords[i]) > 1 and len(keywords[j]) > 1 else 0
                    geo = calculate_geo_score(patents, i, j)                   
                    geo_est = geo_exist(patents, i, j, geo)
                    
                    citing_rp = citing_relationship(patents, i, j)
                    citing_lst_est = citing_rp_est(patents, i, j)[0]
                    cited_lst_est = citing_rp_est(patents, i, j)[1]
                        
                    features_list.append([f'{patents[i]["ida"]}_{patents[j]["ida"]}',
                                          app_i[i][j], app_i_est[i][j], 
                                          app_first_s[i][j], app_first_s_est[i][j], 
                                          co_inventor_i[i][j], co_inventor_i_est[i][j],
                                          ipc_c_i[i][j], ipc_c_i_est[i][j], 
                                          ipc_g_i[i][j], ipc_g_i_est[i][j], 
                                          title[i][j], title_est[i][j], 
                                          kw_sim_1, kw_sim_1_est, 
                                          kw_sim_2, kw_sim_2_est, 
                                          da_s[i][j], da_s_est[i][j], 
                                          geo, geo_est,
                                          citing_rp, citing_lst_est, cited_lst_est])
    else:
        for i in tqdm(range(len(patents)), desc='features processing', total=len(patents)):
            for j in range(i + 1, len(patents)):
                if patents[i]["ida"] != patents[j]["ida"]:
                    geo = calculate_geo_score(patents, i, j)
                    geo_est = geo_exist(patents, i, j, geo)
                    
                    citing_rp = citing_relationship(patents, i, j)
                    citing_lst_est = citing_rp_est(patents, i, j)[0]
                    cited_lst_est = citing_rp_est(patents, i, j)[1]
                    
                    features_list.append([f'{patents[i]["ida"]}_{patents[j]["ida"]}',
                                          app_i[i][j], app_i_est[i][j], 
                                          app_first_s[i][j], app_first_s_est[i][j], 
                                          co_inventor_i[i][j], co_inventor_i_est[i][j],
                                          ipc_c_i[i][j], ipc_c_i_est[i][j], 
                                          ipc_g_i[i][j], ipc_g_i_est[i][j], 
                                          0, 0, 
                                          0, 0, 
                                          0, 0, 
                                          da_s[i][j], da_s_est[i][j], 
                                          geo, geo_est,
                                          citing_rp, citing_lst_est, cited_lst_est])                       

    # 生成feature.json的存储路径
    file_path = json_path.replace('blocks', 'features')
    os.makedirs(file_path.replace(f'{os.path.splitext(os.path.basename(file_path))[0]}.json', ''), exist_ok=True)
    with open(file_path, mode='w', encoding='utf-8') as json_file:
        json.dump({inventor:features_list}, json_file, ensure_ascii = False, indent = 4, sort_keys = False)






if __name__ == "__main__":
    # 加载分词字典
    jieba.load_userdict('raw_data/lexicon.txt')

    # 已有的train数据特征值，把这部分剔除，不必在重复生成
    sample_path = show_files('blocks_sample', [])
    sample_files = [os.path.splitext(os.path.basename(path))[0] for path in sample_path]
    print(sample_files)
    del sample_path
    gc.collect()
    
    # 提取block文件所在文件夹
    blocks_path = show_folders('blocks')
    # thread pool
    with ThreadPoolExecutor(10) as t:
        for jf in tqdm(blocks_path, desc='features processing', total=len(blocks_path)):
            json_lst = show_files(jf, [])
            for block in json_lst:
                if os.path.splitext(os.path.basename(block))[0] not in sample_files:
                    t.submit(process_patents, block)
            
    print('features.json finished.')
 
