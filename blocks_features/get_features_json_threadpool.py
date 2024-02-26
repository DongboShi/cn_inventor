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
    patent_title = patents_data['patent_title']
    ida = patents_data['ida']
    latitude = patents_data['latitude']
    country = patents_data['country']
    inventor_lst = patents_data['inventor_lst']
    citing_lst = patents_data['citing_lst']
    detailed_address = patents_data['detailed_address']
    cited_lst = patents_data['cited_lst']
    road = patents_data['road']
    ipc_class = patents_data['ipc_class']
    applicants_lst = patents_data['applicants_lst']
    longitude = patents_data['longitude']
    province = patents_data['province']
    district = patents_data['district']
    city = patents_data['city']
    ipc_group = patents_data['ipc_group']
    housenumber = patents_data['housenumber']
    app_first = patents_data['app_first']
    del patents_data
    gc.collect()
    start = time.time()
    patents_cp = []
    app_i = []
    app_i_est = []
    app_i_per = []
    app_s = []
    app_s_est = []
    inventor_i = []
    inventor_i_est = []
    inventor_i_per = []
    ipc_c = []
    ipc_c_est = []
    ipc_c_per = []
    ipc_g = []
    ipc_g_est = []
    ipc_g_per = []
    title = []
    title_est = []
    keyword1 = []
    keyword2 = []
    keyword1_est = []
    keyword2_est = []
    geo = []
    geo_est = []
    citing_rp = []
    citing_lst_est = []
    cited_lst_est = []
    diff_days = []
    address_s = []
    address_s_est = []

    if (len(patent_title)!=0) and (all(not s for s in patent_title) != True):
        for i in range(len(patent_title)):
            for j in range(i + 1, len(patent_title)):
                if i != j:
                    patents_cp.append(f'{ida[i]}_{ida[j]}')
                    # app_i
                    app_i_value = lst_intersec(literal_eval(applicants_lst[i]),literal_eval(applicants_lst[j]))
                    app_i.append(app_i_value)
                    app_i_est.append(zeroifs(literal_eval(applicants_lst[i]),literal_eval(applicants_lst[j])))
                    app_i_per.append(max(lst_per(app_i_value, len(literal_eval(applicants_lst[i]))), lst_per(app_i_value, len(literal_eval(applicants_lst[j])))))
                    # app_s
                    app_s.append(match_name_lr(app_first[i], app_first[j]))
                    app_s_est.append(zeroifs(app_first[i], app_first[j]))
                    # inventor_i
                    inventor_i_value = lst_intersec(literal_eval(inventor_lst[i]), literal_eval(inventor_lst[j]))
                    inventor_i.append(inventor_i_value)
                    inventor_i_est.append(zeroifs(literal_eval(inventor_lst[i]), literal_eval(inventor_lst[j])))
                    inventor_i_per.append(max(lst_per(inventor_i_value, len(literal_eval(inventor_lst[i]))),
                                         lst_per(inventor_i_value, len(literal_eval(inventor_lst[j])))))
                    # ipc_c
                    ipc_c_value = lst_intersec(literal_eval(ipc_class[i]), literal_eval(ipc_class[j]))
                    ipc_c.append(ipc_c_value)
                    ipc_c_est.append(zeroifs(literal_eval(ipc_class[i]), literal_eval(ipc_class[j])))
                    ipc_c_per.append(max(lst_per(ipc_c_value, len(literal_eval(ipc_class[i]))),
                                              lst_per(ipc_c_value, len(literal_eval(ipc_class[j])))))

                    # ipc_g
                    ipc_g_value = lst_intersec(literal_eval(ipc_group[i]), literal_eval(ipc_group[j]))
                    ipc_g.append(ipc_g_value)
                    ipc_g_est.append(zeroifs(literal_eval(ipc_group[i]), literal_eval(ipc_group[j])))
                    ipc_g_per.append(max(lst_per(ipc_g_value, len(literal_eval(ipc_group[i]))),
                                              lst_per(ipc_g_value, len(literal_eval(ipc_group[j])))))

                    # title
                    title.append(match_name_lr(patent_title[i], patent_title[j]))
                    title_est.append(zeroifs(patent_title[i], patent_title[j]))
                    # keywords
                    keywords_i = extract_tags(patent_title[i], topK=2)
                    keywords_j = extract_tags(patent_title[j], topK=2)
                    for keywords in [keywords_i, keywords_j]:
                        if len(keywords) < 2:
                            keywords += [None] * (2 - len(keywords))
                    keyword1.append(match_name_lr(keywords_i[0], keywords_j[0]))
                    keyword2.append(match_name_lr(keywords_i[1], keywords_j[1]))
                    keyword1_est.append(zeroifs(keywords_i[0], keywords_j[0]))
                    keyword2_est.append(zeroifs(keywords_i[1], keywords_j[1]))
                    # geo
                    geo_value = calculate_geo_score(i, j, country, province, city, district, road, latitude, longitude)
                    geo.append(geo_value)
                    geo_est.append(geo_exist(i, j, geo_value, country, province, city, district, road, latitude, longitude))
                    # citing
                    citing_rp.append(citing_relationship(i, j, citing_lst, cited_lst, ida))
                    citing_lst_est.append(citing_rp_est(i, j, citing_lst, cited_lst)[0])
                    cited_lst_est.append(citing_rp_est(i, j, citing_lst, cited_lst)[1])
                    # diff_days
                    adate_i = np.datetime64(cnp_pnr_ida_dict.get(ida[i], '9999-12-31'))
                    adate_j = np.datetime64(cnp_pnr_ida_dict.get(ida[j], '9999-12-31'))
                    diff_days.append(np.abs(adate_i - adate_j).astype('timedelta64[D]').astype(int))
                    # address_s
                    address_s.append(match_name_lr(detailed_address[i], detailed_address[j]))
                    address_s_est.append(zeroifs(detailed_address[i], detailed_address[j]))
    print(f'{scientist_folder} calculation costs {time.time()-start}s')
    features_data = {}
    features_data['patents_cp'] = patents_cp
    features_data['app_i'] = app_i
    features_data['app_i_est'] = app_i_est
    features_data['app_i_per'] = app_i_per
    features_data['app_s'] = app_s
    features_data['app_s_est'] = app_s_est
    features_data['inventor_i'] = inventor_i
    features_data['inventor_i_est'] = inventor_i_est
    features_data['inventor_i_per'] = inventor_i_per
    features_data['ipc_c'] = ipc_c
    features_data['ipc_c_est'] = ipc_c_est
    features_data['ipc_c_per'] = ipc_c_per
    features_data['ipc_g'] = ipc_g
    features_data['ipc_g_est'] = ipc_g_est
    features_data['ipc_g_per'] = ipc_g_per
    features_data['title'] = title
    features_data['title_est'] = title_est
    features_data['keyword1'] = keyword1
    features_data['keyword2'] = keyword2
    features_data['keyword1_est'] = keyword1_est
    features_data['keyword2_est'] = keyword2_est
    features_data['geo'] = geo
    features_data['geo_est'] = geo_est
    features_data['citing_rp'] = citing_rp
    features_data['citing_lst_est'] = citing_lst_est
    features_data['cited_lst_est'] = cited_lst_est
    features_data['diff_days'] = diff_days
    features_data['address_s'] = address_s
    features_data['address_s_est'] = address_s_est
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
               'citing_rp', 'citing_lst_est', 'cited_lst_est', 'diff_days']
if __name__ == "__main__":
    blocks_lst = show_folders('blocks_total_split')
    cnp_pnr_ida = pd.read_csv('../cnp_pnr_ida.csv')
    cnp_pnr_ida_dict = dict(zip(cnp_pnr_ida['ida'], cnp_pnr_ida['adate']))
    del cnp_pnr_ida
    gc.collect()

    with ThreadPoolExecutor(16) as t:
        for jf in blocks_lst:
            t.submit(process_patents, jf, cnp_pnr_ida_dict, key_lst)

    print('features_total_split finished.')
