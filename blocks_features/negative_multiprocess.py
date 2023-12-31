import pandas as pd
import os
from tqdm import tqdm
import gc
import numpy as np
from multiprocessing import Pool

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

# 合并所有feature数据
def features_merge(inventor_folder, scientists_date_lst, cnp_pnr_ida_dict):
    try:
        sorted_files = [f'{inventor_folder}/{key}.txt' for key in key_lst]
        combined_data = []

        with open(f'{inventor_folder}/patents_cp.txt', 'r', encoding="utf-8") as load_f:
            pair_n_lst = []
            diff_days_lst = []
            f_lines = load_f.readlines()
            for pair in f_lines:
                patents = pair.strip().split('_')
                if (patents[0] in scientists_date_lst) and (patents[1] not in scientists_date_lst) and (
                        patents[1] in cnp_pnr_ida_dict):
                    adate1 = np.datetime64(cnp_pnr_ida_dict[patents[1]])
                    if adate1 <= np.datetime64('2018-12-31'):
                        pair_n_lst.append(f_lines.index(pair))
                        adate0 = np.datetime64(cnp_pnr_ida_dict[patents[0]])
                        diff_days_lst.append((adate0 - adate1).astype('timedelta64[D]').astype(int).astype(str))
                elif (patents[1] in scientists_date_lst) and (patents[0] not in scientists_date_lst) and (
                        patents[0] in cnp_pnr_ida_dict):
                    adate0 = np.datetime64(cnp_pnr_ida_dict[patents[0]])
                    if adate0 <= np.datetime64('2018-12-31'):
                        pair_n_lst.append(f_lines.index(pair))
                        adate1 = np.datetime64(cnp_pnr_ida_dict[patents[1]])
                        diff_days_lst.append((adate0 - adate1).astype('timedelta64[D]').astype(int).astype(str))
        feature_lst = []
        for file in sorted_files:
            with open(file, 'r', encoding="utf-8") as f:
                content = f.readlines()
                feature_lst.append([content[p] for p in pair_n_lst if p < len(content)])
        feature_lst.append(diff_days_lst)

        for row in zip(*feature_lst):
            combined_data.append([os.path.basename(inventor_folder)] + [item.strip() for item in row])
        print(f'{inventor_folder} finished. {len(diff_days_lst)} rows.')
        return combined_data
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