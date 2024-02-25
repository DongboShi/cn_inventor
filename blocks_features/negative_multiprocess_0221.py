#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :negative_multiprocess_0221.py
# @Time      :2024/2/21 16:38
# @Author    :YanjunDing, FanZhang

# 基于negative_multiprocess.py文件，进行了运行速率提升的优化
# 主要方法为提取process_file函数，以实现多进程和多线程混合处理；以及其他函数调用的细节优化
# 参考了https://cloud.tencent.com/developer/article/1853708

import pandas as pd
import os
import gc
import numpy as np
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
import time

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

# 查询文件夹下所有子文件夹
def show_folders(path):
    all_scientist_folder = []
    for root, folder, file in os.walk(path):
        if len(folder) == 0 and len(file)>0:
            all_scientist_folder.append(root)
    return all_scientist_folder

# 把这部分提取出来，方便在后面进行多线程处理
def process_file(file, pair_lst):
    try:
        with open(file, 'r', encoding="utf-8") as f:
            content = f.readlines()
        # 从文件路径中提取文件名（不包含扩展名），用作特征名称
        feature_name = os.path.splitext(os.path.basename(file))[0]
        # 生成特征值列表，根据pair_n_lst索引选择行，注意行索引从0开始
        feature_values = [content[p].strip() for p in pair_lst if p < len(content)]
        # 返回特征名称和对应的特征值列表
        return feature_name, feature_values

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

# 合并所有feature数据
def features_merge(inventor_folder, scientists_date_lst, cnp_pnr_ida_dict):
    try:
        # 根据提供的key_lst构建文件路径列表
        sorted_files = [f'{inventor_folder}/{key}.txt' for key in key_lst]

        # 存储符合条件的专利申请号和日期差值
        pair_n_lst = []
        diff_days_lst = []

        with open(os.path.join(inventor_folder, 'patents_cp.txt'), 'r', encoding="utf-8") as load_f:
            for i, pair in enumerate(load_f):
                patents = pair.strip().split('_')  # 根据下划线拆分专利号
                check_dates = [np.datetime64(cnp_pnr_ida_dict.get(patent, '9999-12-31')) for patent in
                               patents]  # 获取日期并转换成np.datetime64类型
                if all(patent in cnp_pnr_ida_dict for patent in patents) and (
                        (patents[0] in scientists_date_lst) != (patents[1] in scientists_date_lst)):  # 检查日期是否符合条件
                    adate0, adate1 = check_dates
                    if (adate0 <= np.datetime64('2018-12-31')) or (  # 阳性样本都是2018-12-31之前的专利
                            adate1 <= np.datetime64('2018-12-31')):  # 如果日期早于等于2018-12-31
                        pair_n_lst.append(i)
                        diff_days = np.abs(adate0 - adate1).astype('timedelta64[D]').astype(int)  # 计算日期差值
                        diff_days_lst.append(str(diff_days))  # 将日期差值添加到列表中

        feature_data = []
        with ThreadPoolExecutor(max_workers=12) as executor:
            # 提交所有文件处理任务，并保留futures以保持顺序
            futures = [executor.submit(process_file, file, pair_n_lst) for file in sorted_files]
            # 按提交顺序获取future结果
            for future in futures:
                try:
                    # 尝试解包future的结果
                    feature_name, feature_values = future.result()
                    feature_data.append((feature_name, feature_values))
                except ValueError as e:
                    print(f"Error unpacking future result: {e}")

        # 添加diff_days_lst到特征列表中
        feature_data.append(('diff_days', diff_days_lst))

        # 解包特征名称和值
        _, features_values = zip(*feature_data)

        # 使用zip转置特征值列表，然后构建每一行的数据
        combined_data = [[os.path.basename(inventor_folder)] + list(values) for values in zip(*features_values)]
        # 控制多线程输出结果最后合并的排列顺序
        end = time.time()
        print(f'{inventor_folder} finished. {len(diff_days_lst)} rows. Cost {end - start}s.')
        return combined_data  # 返回组合数据

    # 异常情况处理
    except Exception as e:
        print(f"Error in {inventor_folder}: {e}")
        return []

def features_df(features_all_path, scientists_date_lst, cnp_pnr_ida_dict):
    try:
        features_files = show_folders(features_all_path)
        combined_data = []
        pool_size = 12

        with Pool(pool_size) as p:
            results = p.starmap(features_merge, [(feature_json, scientists_date_lst, cnp_pnr_ida_dict) for feature_json in features_files])

        for result in results:
            combined_data.extend(result)

        df = pd.DataFrame(combined_data, columns=['inventor'] + key_lst + ['diff_days'])
        return df
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()


key_lst = ['patents_cp', 'app_i', 'app_i_est', 'app_s', 'app_s_est',
               'inventor_i', 'inventor_i_est',
               'ipc_c', 'ipc_c_est',
               'ipc_g', 'ipc_g_est',
               'title', 'title_est',
               'keyword1', 'keyword1_est',
               'keyword2', 'keyword2_est',
               'address_s', 'address_s_est',
               'geo', 'geo_est',
               'citing_rp', 'citing_lst_est', 'cited_lst_est']


if __name__ == '__main__':

    # merge date
    scientists = pd.read_csv('raw_data/scientists_nmclean.csv')
    cnp_pnr_ida = pd.read_csv('../cnp_pnr_ida.csv')
    cnp_pnr_ida_dict = cnp_pnr_ida[["ida", "adate"]].set_index("ida").to_dict(orient='dict')["adate"]
    cnp_pnr_ida = cnp_pnr_ida[['ida','adate']].copy()
    scientists_date = pd.merge(scientists, cnp_pnr_ida[['ida','adate']], on = 'ida', how = 'left')
    scientists_date = scientists_date[scientists_date['adate'].notnull()].copy()
    scientists_date_lst = scientists_date['ida'].tolist()
    del cnp_pnr_ida
    del scientists_date
    gc.collect()
    # 合并features
    features_data = features_df('features_split_sample', scientists_date_lst, cnp_pnr_ida_dict)
    features_data.to_csv('clean_data/features_scientists_neg.csv', index = False, encoding='utf-8')
    print('features dataframe finished.')
