# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 13:38:18 2023

@author: Killlua
"""

import pandas as pd
import re
import csv
import gc
from tqdm import tqdm

# read cn_ipc.txt
# define columns
column_names = ['ida', 'ipc']  # 根据实际列数更改

df = pd.read_csv('../cn_ipc.txt', sep='|', header=None, names=column_names)
df['ida'] = df['ida'].apply(lambda x: ''.join([x.split('-')[0], x.split('-')[1]]))
df['ipc_group'] = df['ipc'].apply(lambda x: re.search(r'(\w\d*)/', x).group(1) if re.search(r'(\w\d*)/', x) else None)
df['ipc_class'] = df['ipc'].apply(lambda x: re.search(r'(\w\d+)', x).group(1) if re.search(r'(\w\d+)', x) else None)

# ouput
df.to_csv('cn_ipc_new.csv', sep=',', index = False)
print('======================cn_ipc_new.csv finished.======================')
# read cn_title.txt
with open('../cn_title.txt',mode = 'r',encoding = 'utf-8') as f:
    reader = csv.reader(f, delimiter='|')
    data = []
    for row in reader:
        if len(row) > 2:
            # Handle the problematic row
            new_row = row[0], ''.join(row[1:]).replace(',', '_')
        else:
            new_row = row[0], row[1].replace(',', '_')
        data.append(new_row)

df = pd.DataFrame(data,columns=['ida', 'patent_title'])
df['ida'] = df['ida'].apply(lambda x: ''.join([x.split('-')[0], x.split('-')[1]]))
# ouput
df.to_csv('cn_title_new.csv', sep=',', index = False)
print('======================cn_title_new.csv finished.======================')

# read app_pub_number.txt
column_names = ['pnr','ida','country','kind','pct','fmlyid']
with open('../app_pub_number.txt',mode = 'r',encoding = 'utf-8') as f:
    reader = csv.reader(f, delimiter='|')
    data = []
    for row in reader:
        data.append(row)

df = pd.DataFrame(data,columns=column_names)
df_n = df[(df['ida'].notnull()) | (df['ida']!= '')]
print(f'app_pub_number_notnull.txt is not empty, {df_n.shape[0]} rows.')
df_n['ida'] = df_n['ida'].apply(lambda x: ''.join(x.split('-')[0:2]))
df_n = df_n[(df_n['kind'] == 'A')|(df_n['kind'] == 'B')|(df_n['kind'] == 'C')]
assert(df_n.empty == False)
print(f'app_pub_number_filter.txt is not empty, {df_n.shape[0]} rows.')
df_n.drop_duplicates('ida', keep = 'first',inplace = True)
df_n.to_csv('app_pub_number_new.csv', sep=',', index = False)

df_cn = df_n[df_n['ida'].str.startswith('CN')]
df_sp = df_cn.iloc[0:3000,:]

invent_patents = df_n['ida'].unique()
invent_patents_sp = df_sp['ida'].unique()
del df
del df_n
del df_cn
del df_sp
del column_names
gc.collect()

names = locals()
df_lst = ['inventor', 'cn_ipc', 'cn_title', 'applicant', 'formatted_address_1110']
for i in tqdm(df_lst, desc='data processing', total=len(df_lst)):
    if (i == 'cn_ipc') or (i == 'cn_title'):
        names[i] = pd.read_csv(f'{i}_new.csv', sep=',')
    else:
        names[i] = pd.read_csv(f'../{i}.csv', sep=',')
        
    names[i] = names[i][names[i]['ida'].isin(invent_patents)].copy()
    assert(names[i].empty == False)
    print(f'{i} is not empty, {names[i].shape[0]} rows.')
    names[i].to_csv(f'{i}_new.csv', sep=',', index = False)
    # sample
    sp = names[i][names[i]['ida'].isin(invent_patents_sp)].copy()
    assert(sp.empty == False)
    print(f'{i}_split is not empty, {sp.shape[0]} rows.')
    sp.to_csv(f'{i}_new_sp.csv', sep=',', index = False)
    del names[i]
    del sp
    gc.collect()

# 由于cn_e_cite_all.csv晚于其他文件上传，此处代码是后接在原代码后新跑的
app_pub_number = pd.read_csv('raw_data/app_pub_number_new.csv', sep=',', encoding='utf-8')

df_cn = app_pub_number[app_pub_number['ida'].str.startswith('CN')]
df_sp = df_cn.iloc[0:3000,:]

invent_patents = app_pub_number['ida'].unique()
invent_patents_sp = df_sp['ida'].unique()
del app_pub_number
del df_cn
del df_sp
gc.collect()

citing = pd.read_csv('../cn_e_cite_all.csv', sep=',', encoding='utf-8')
citing['citing_ida'] = citing['citing_ida'].apply(lambda x: re.search(r'(\w*\d+)', x).group(0) if (isinstance(x,str)) and (re.search(r'(\w*\d+)', x)) else None)
citing['cited_ida'] = citing['cited_ida'].apply(lambda x: re.search(r'(\w*\d+)', x).group(0) if (isinstance(x,str)) and (re.search(r'(\w*\d+)', x)) else None)
print(f'citing is not empty, {citing.shape[0]} rows.')
citing.to_csv(f'raw_data/cn_e_cite_all_new.csv', sep=',', index = False)
# sample
sp = citing[citing['citing_ida'].isin(invent_patents_sp)].copy()
assert(sp.empty == False)
print(f'citing_split is not empty, {sp.shape[0]} rows.')
sp.to_csv(f'raw_data/cn_e_cite_all_new_sp.csv', sep=',', index = False)

