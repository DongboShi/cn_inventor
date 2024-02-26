import gc

import pandas as pd
import os
from tqdm import tqdm
import json
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

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

# 拆分features
def features_split(f_path):
    try:
        with open(f_path, mode='r', encoding='utf-8') as fq:
            features = json.load(fq)
            inventor = list(features.keys())[0]
        folder_path = f_path.replace('features', 'features_split').replace('.json', '')
        os.makedirs(folder_path, exist_ok=True)
        for inv in features:
            count = 0
            for features_need in key_lst:
                feature_need_str = ""
                for f in features[inv]:
                    feature_need_str = feature_need_str + f'{f[count]}\n'
                with open(f'{folder_path}/{features_need}.txt', mode='w', encoding='utf-8') as f_file:
                    f_file.write(feature_need_str)
                count += 1
    except Exception as e:
        print(f"Error: {e}")

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
def features_merge(inventor_folder, patents_cp_dict):
    try:
        start = time.time()
        sorted_files = [f'{inventor_folder}/{key}.txt' for key in key_lst]
        pair_lst = []
        diff_days_lst = []
        with open(f'{inventor_folder}/patents_cp.txt', 'r', encoding="utf-8") as load_f:
            for i, pair in enumerate(load_f):
                patents = pair.strip().split('_')
                pair_key = f'{patents[0]}_{patents[1]}'
                reverse_pair_key = f'{patents[1]}_{patents[0]}'
                diff_days = patents_cp_dict.get(pair_key) or patents_cp_dict.get(reverse_pair_key)

                if diff_days is not None:
                    pair_lst.append(i)
                    diff_days_lst.append(str(diff_days))

        feature_data = []
        with ThreadPoolExecutor(max_workers=12) as executor:
            # 提交所有文件处理任务，并保留futures以保持顺序
            futures = [executor.submit(process_file, file, pair_lst) for file in sorted_files]
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
        end = time.time()
        print(f'{inventor_folder} finished. {len(diff_days_lst)} rows. Cost {end-start}s.')
        return combined_data  # 返回组合数据

    except Exception as e:
        print(f"Error in {inventor_folder}: {e}")
        return []

def features_df(features_all_path, patents_cp_dict):
    try:
        features_files = show_folders(features_all_path)
        # 调用了show_folders函数，以获取特征文件夹中的所有子文件夹
        combined_data = []

        with ProcessPoolExecutor(max_workers=12) as executor:
            futures = [
                executor.submit(features_merge, feature_json, patents_cp_dict) for
                feature_json in features_files]
            for future in futures:
                result = future.result()
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

    # feature_files_path = show_files('features_sample', [])
    # with ThreadPoolExecutor(12) as t:
    #     for i in tqdm(feature_files_path, desc='features_split', total=len(feature_files_path)):
    #         t.submit(features_split, i)
    # merge date
    scientists = pd.read_csv('raw_data/scientists_nmclean.csv')
    cnp_pnr_ida = pd.read_csv('../cnp_pnr_ida.csv')
    cnp_pnr_ida['adate'] = cnp_pnr_ida['adate'].astype('datetime64[ns]')
    scientists_date = pd.merge(scientists, cnp_pnr_ida[['ida','adate']], on = 'ida', how = 'left')
    scientists_date['adate'] = scientists_date['adate'].astype('datetime64[ns]')
    scientists_date = scientists_date[scientists_date['adate'].notnull()].copy()
    # generate patent_pairs

    patents_cp_dict = {}
    for inv in scientists_date['Name'].unique():
        inv_data = scientists_date[scientists_date['Name']==inv].copy().reset_index(drop = True)
        if len(inv_data) > 1:
            for i in tqdm(range(len(inv_data)), desc='patent pair', total=len(inv_data)):
                for j in range(i + 1, len(inv_data)):
                    diff_days = (inv_data.loc[i, 'adate'] - inv_data.loc[j, 'adate']).days
                    patents_cp_dict[f'{inv_data.loc[i,"ida"]}_{inv_data.loc[j,"ida"]}'] = diff_days

    del scientists_date
    gc.collect()

    # 合并features
    features_data = features_df('features_split_sample', patents_cp_dict)
    features_data.to_csv('clean_data/features_scientists_pos_new.csv', index=False, encoding='utf-8')

    print('features dataframe finished.')