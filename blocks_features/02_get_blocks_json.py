# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 20:45:36 2023

@author: Killlua
"""

from collections import defaultdict
from tqdm import tqdm
import csv
import os
import shutil
import json
import re
import gc

from concurrent.futures import ThreadPoolExecutor

# scientist's name as filename, replace characters that don't fit into the filename with '_'
def replace_special_chars(string):
    pattern = r'[\\/:*?"<>|,]'
    return re.sub(pattern, '_', string)

def create_folder_path(index):
    # Calculate folder indices for each level
    indices = [0] * depth
    for i in range(depth - 1, -1, -1):
        indices[i] = index % folders_per_level
        index //= folders_per_level

    # Create the folder path
    folder_path = base_dir
    for idx in indices:
        folder_path = os.path.join(folder_path, f'folder_{idx}')

    return folder_path

# save every block in json file
def save_blocks_json(index):
    folder_index = index // files_per_folder
    folder_path = create_folder_path(folder_index)
    os.makedirs(folder_path, exist_ok=True)

    # Create the file path
    inventor_raw = list(blocks.keys())[index]
    inventor = replace_special_chars(inventor_raw)
    file_path = os.path.join(folder_path, f'{inventor}.json')
    # Create json file
    with open(file_path, mode='w', encoding='utf-8') as json_file:
        json.dump({inventor_raw:blocks[inventor_raw]}, json_file, ensure_ascii = False, indent = 4, sort_keys = False)
        


if __name__ == "__main__":

    
    inventor = []
    with open(r'raw_data/inventor_new.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            inventor.append(row)
    
    
    # take inventors
    inventor_lst = defaultdict(list)
    for i in inventor:
        inventor_lst[i['ida']].append(i['inventor'])
            
    # construct blocks
    blocks = defaultdict(list)
    for inv in inventor:
        if (inv['inventor']!='要求不公布姓名') and (inv['inventor']!='不公告发明人'):
            blocks[inv['inventor']].append({'ida':inv['ida'], 'inventor_lst':inventor_lst[inv['ida']]})
    
    # blocks finished, clean inventor
    del inventor
    gc.collect()
    print('pre_blocks finished.')

    # applicants
    applicants = []
    with open(r'raw_data/applicant_new.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            applicants.append(row)
    # app_i
    applicants_lst = defaultdict(list)
    for i in applicants:
        applicants_lst[i['ida']].append(i['applicant'])
        
    # take 1st applicant
    dict_app_st = {}
    for i in applicants:
        ida = i['ida']
        app_sq = int(i['applicant_seq'])
        if app_sq == 1:
            dict_app_st[ida] = i['applicant']
            
    del applicants
    gc.collect()
    print('features about applicants finished.')
    
    # import cn_ipc
    cn_ipc = []
    with open(r'raw_data/cn_ipc_new.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            cn_ipc.append(row)
            
    # ipc_group & ipc_class
    dict_cn_ipc = defaultdict(dict)
    for ipc in cn_ipc:
        dict_cn_ipc[ipc['ida']]['ipc_class']= []
        dict_cn_ipc[ipc['ida']]['ipc_group']= []
        
    for ipc in cn_ipc:
        dict_cn_ipc[ipc['ida']]['ipc_class'].append(ipc['ipc_class'])
        dict_cn_ipc[ipc['ida']]['ipc_group'].append(ipc['ipc_group'])
        
    del cn_ipc
    gc.collect()
    print('features about ipc finished.')

    # import cn_title
    cn_title = []
    with open(r'raw_data/cn_title_new.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            cn_title.append(row)
    
    # title features
    dict_cn_title = {}
    for title in cn_title:
        dict_cn_title[title['ida']]= title['patent_title']

    
    del cn_title
    gc.collect()
    print('features about title finished.')
        
    # import address
    address = []
    with open(r'raw_data/formatted_address_1110_new.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            address.append(row)
            
    dict_address = defaultdict(dict)
    for a in address:
        dict_address[a['ida']]['detailed_address'] = a['详细地址']
        dict_address[a['ida']]['country'] = a['国家']
        dict_address[a['ida']]['province'] = a['省份']
        dict_address[a['ida']]['city'] = a['城市']
        dict_address[a['ida']]['district'] = a['地址所在的区']
        dict_address[a['ida']]['road'] = a['街道']
        dict_address[a['ida']]['housenumber'] = a['门牌']
        dict_address[a['ida']]['latitude'] = a['纬度']
        dict_address[a['ida']]['longitude'] = a['经度']

    del address
    gc.collect()
    print('features about address finished.')
    a = 0
    b = 0
    for i in dict_address:
        if (dict_address[i]['country']=='') and (dict_address[i]['province']!=''):
            a+=1
        if (dict_address[i]['country']=='') and (dict_address[i]['province']=='') and (dict_address[i]['city']!=''):
            b+=1
    print(f'{a} data countries are empty and provinces are not; {b} data countries and provinces are empty and cities are not.')
    
    # citing
    citing = []
    with open(r'raw_data/cn_e_cite_all_new.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            citing.append(row)
    # citing_lst
    citing_lst = defaultdict(list)
    for i in citing:
        citing_lst[i['citing_ida']].append(i['cited_ida'])
    
    cited_lst = defaultdict(list)
    for i in citing:
        cited_lst[i['cited_ida']].append(i['citing_ida'])
                    
    del citing
    gc.collect()
    print('features about citing finished.')
   # complete blocks
    for block in blocks:
        for item in blocks[block]:
            item['applicants_lst'] = applicants_lst.get(item['ida'])
            item['app_first']= dict_app_st.get(item['ida'])
            item['ipc_class'] = dict_cn_ipc[item['ida']].get('ipc_class')
            item['ipc_group'] = dict_cn_ipc[item['ida']].get('ipc_group')
            item['patent_title'] = dict_cn_title.get(item['ida'])
            item['citing_lst'] = citing_lst.get(item['ida'])
            item['cited_lst'] = cited_lst.get(item['ida'])
            if dict_address.get(item['ida']):
                item['detailed_address'] = dict_address.get(item['ida'])['detailed_address']
                item['country'] = dict_address.get(item['ida'])['country']
                item['province'] = dict_address.get(item['ida'])['province']
                item['city'] = dict_address.get(item['ida'])['city']
                item['district'] = dict_address.get(item['ida'])['district']
                item['road'] = dict_address.get(item['ida'])['road']
                item['housenumber'] = dict_address.get(item['ida'])['housenumber']
                item['latitude'] = dict_address.get(item['ida'])['latitude']
                item['longitude'] = dict_address.get(item['ida'])['longitude']
            else:
                item['detailed_address'] = ''
                item['country'] = ''
                item['province'] = ''
                item['city'] = ''
                item['district'] = ''
                item['road'] = ''
                item['housenumber'] = ''
                item['latitude'] = ''
                item['longitude'] = ''
    
    print('blocks finished.')
    del applicants_lst
    del dict_app_st
    del dict_cn_ipc
    del dict_cn_title
    del citing_lst
    del cited_lst
    del dict_address
    gc.collect()
    
    # delete inventors who only have one patent
    del_inventors = []
    for inventor, patents in tqdm(blocks.items(), desc='block_del_sole_patent', total=len(blocks.items())):
        if len(patents) <= 1:
            del_inventors.append(inventor)
    
    for i in del_inventors:
        blocks.pop(i, 'pop失败')
    
    del del_inventors
    gc.collect()
    
    # create folders
    files_per_folder=100
    folders_per_level=100
    base_dir='blocks'
    total_elements = len(blocks)
    depth = 0
    while total_elements > 0:
        total_elements = total_elements // (files_per_folder * folders_per_level)
        depth += 1
    
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir, exist_ok=True)


    # thread pool
    with ThreadPoolExecutor(10) as t:
        for index in tqdm(range(len(blocks)), desc='block processing', total=len(blocks)):
            t.submit(save_blocks_json, index)
    
    print('blocks json files finished.')
