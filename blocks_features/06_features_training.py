import pandas as pd
import os
import gc
import glob
from tqdm import tqdm
import json
import jieba.analyse
import shutil
from get_features_json_threadpool import show_files, process_patents
from get_blocks_json import replace_special_chars
from concurrent.futures import ThreadPoolExecutor, as_completed


# 清洗专利申请号
def applicant_num_clean(s):
    if 'PCT/' in s:
        applicant_num = s.replace('PCT/','')
    elif (s.startswith('ZL')) and ('.' in s):
        applicant_num = ''.join(s.replace('ZL','CN').split('.')[0:-1])
    elif (s.startswith(':')) and (s.replace(':','')[0].isdigit()):
        applicant_num = f'CN{"".join(s.replace(":","").split(".")[0:-1])}'
    elif (s.startswith(':')==False) and (':' in s):
        applicant_num = ''.join(s.replace(':','.').replace(' ','').split('.')[0:-1])
    elif '-' in s:
        applicant_num = s.replace('-','')
    elif (s[0].isdigit()) and ('.' in s):
        applicant_num = f'CN{"".join(s.split(".")[0:-1])}'
    elif (s.startswith('ZL')) and ('.' not in s):
        applicant_num = s.replace('ZL','CN')[0:-1]
    elif (s.startswith('CN')) and ('.' in s):
        applicant_num = ''.join(s.split('.')[0:-1])
    else:
        applicant_num = s
    return applicant_num

# 创建多层文件夹
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

# 查找文件路径
def find_file(root_folder, file_name):
    for folder, _, files in os.walk(root_folder):
        if file_name in files:
            return os.path.join(folder, file_name)
    return None

def blocks_split(b_path):
    with open(b_path, mode='r', encoding='utf-8') as f:
        block = json.load(f)
        inventor = list(block.keys())[0]
    folder_path = b_path.replace('blocks', 'blocks_split').replace('.json', '')
    os.makedirs(folder_path, exist_ok=True)
    with open(f'features_need.txt', mode='r', encoding='utf-8') as f:
        for line in f.readlines():
            feature_need = line.replace('\n', '')
            feature_need_str = ""
            for fea in block[inventor]:
                feature_need_str = feature_need_str + f'{fea[feature_need]}\n'
            with open(f'{folder_path}/{feature_need}.txt', mode='w', encoding='utf-8') as b_file:
                b_file.write(feature_need_str)

def blocks_copy(scientist_name):
    file_path_lst = glob.glob(f"**/{scientist_name}.json", recursive=True)
    if len(file_path_lst)==1 and file_path_lst[0].startswith('blocks'):
        block_file_path = file_path_lst[0]
        blocks_split(block_file_path)

# 合并所有feature数据
def features_merge(feature_json, combined_data):
    with open(feature_json,'r',encoding = "utf-8") as load_f:
        features = json.load(load_f)
    for st in features:
        for feature_lst in features[st]:
            combined_data.append([st] + feature_lst)


# 多线程合并features文件
def features_csv(features_all_path):
    features_files = show_files(features_all_path, [])
    combined_data = []
    with ThreadPoolExecutor(6) as t:
        futures = []
        for feature_json in features_files:
            future = t.submit(features_merge, feature_json, combined_data)
            futures.append(future)

        for future in as_completed(futures):
            future.result()
    # 生成features的csv文件。后续测试集省略这一步
    with open('clean_data/features_df_all_test.csv', mode='w', encoding='utf-8') as fe:
        fe.write('inventor,patents_cp,app_i,app_i_est,app_s,app_s_est,inventor_i,inventor_i_est,ipc_c,ipc_c_est,ipc_g,ipc_g_est,title,title_est,keyword1,keyword1_est,keyword2,keyword2_est,address_s,address_s_est,geo,geo_est,citing_rp,citing_lst_est,cited_lst_est\n')
        for row in combined_data:
            fe.write(','.join(map(str, row)) + '\n')

jieba.load_userdict('raw_data/lexicon.txt')
if __name__ == '__main__':
    # 稀有姓名集
    rarename_lst0 = []
    with open('../rarename_list_xmzj_1123.csv', mode = 'r', encoding = 'utf-8') as f:
        for line in f.readlines():
            rarename_lst0.append(replace_special_chars(line.split(',')[1]).replace('\n',''))

    # 提取所有block文件路径和发明家名
    block_files_path = show_files('blocks_sample', [])
    block_files = [os.path.splitext(os.path.basename(path))[0] for path in block_files_path]

    del block_files_path
    gc.collect()

    rarename_sample0 = list(set(rarename_lst0) & set(block_files))

    with ThreadPoolExecutor(10) as t:
        for i in tqdm(block_files, desc='save_rare_name_blocks_sample',total=len(block_files)):
            t.submit(blocks_copy,i)


    #
    #
    # scientist0 = pd.read_csv('../scientist.csv')
    # scientist1 = pd.read_csv('raw_data/scientists2.csv', encoding='utf-8')
    # app_pub_number = pd.read_csv('raw_data/app_pub_number_new.csv', sep=',', encoding='utf-8')
    # # 清洗app_pub_number中的专利公开号
    # app_pub_number['专利公开号'] = app_pub_number['pnr'].apply(lambda x: x.replace('-', '') if '-' in x else x)
    # # scientist0专利申请号申请
    # scientist0['ida'] = scientist0['patent'].apply(lambda x: applicant_num_clean(x))
    # scientist0 = scientist0[['ida', 'ID', 'Name']]
    # # 提取处理后的申请号能够和app_pub_number中的专利申请号匹配的部分
    # scientist0_match = scientist0[scientist0['ida'].isin(app_pub_number['ida'])]
    # # 提取无法和app_pub_number中的专利申请号匹配的部分
    # scientist0_notmatch = scientist0[~scientist0['ida'].isin(app_pub_number['ida'])]
    # # 发现部分申请号实际上是公开号，和app_pub_number中的专利公开号匹配获取申请号
    # scientist0_notmatch = pd.merge(scientist0_notmatch,app_pub_number[['ida','专利公开号']],
    #                                left_on='ida', right_on='专利公开号', how = 'left', suffixes=('','_0'))
    # # 可能有部分公开号未被处理，与app_pub_number中的未处理过的公开号匹配获取申请号
    # scientist0_notmatch = pd.merge(scientist0_notmatch, app_pub_number[['ida', 'pnr']],
    #                                left_on='ida', right_on='pnr', how='left', suffixes=('', '_1'))
    # scientist0_notmatch['ida_0'].fillna(scientist0_notmatch['ida_1'], inplace=True)
    # # 提取成功用公开号匹配到申请号的部分
    # scientist0_notmatch_pnr = scientist0_notmatch[scientist0_notmatch['ida_0'].notnull()].copy()
    # # 提取仍然无法匹配到申请号的部分
    # scientist0_notmatch_pnr_n = scientist0_notmatch[scientist0_notmatch['ida_0'].isnull()].copy()
    # # 清洗因merge产生的重复值
    # scientist0_notmatch_pnr.drop_duplicates(subset=['ida_0', 'ID', 'Name'],keep='first',inplace=True, ignore_index=True)
    # scientist0_notmatch_pnr_n.drop_duplicates(subset=['ida', 'ID', 'Name'], keep='first', inplace=True, ignore_index=True)
    # scientist0_notmatch_pnr = scientist0_notmatch_pnr[['ida_0', 'ID', 'Name']].copy()
    # # 更改已有申请号的部分的列名，用于和第一次直接用申请号匹配到的部分合并
    # scientist0_notmatch_pnr.columns = ['ida', 'ID', 'Name']
    # scientist0 = pd.concat([scientist0_match,scientist0_notmatch_pnr], ignore_index=True)
    # scientist0.drop_duplicates(subset=['ida', 'ID', 'Name'], keep='first', inplace=True, ignore_index=True)
    # # 导出申请号无法匹配的部分（多为国外专利或U型专利）
    # scientist0_notmatch_pnr_n.to_csv('raw_data/scientist0_notmatch_pnr_n.csv',index = False, encoding = 'utf-8_sig')
    #
    # # 清洗scientist1
    # scientist1.loc[scientist1['专利公开号'] == 'CN105584990', '专利公开号'] = 'CN105584990B'
    # scientist1 = pd.merge(scientist1, app_pub_number[['专利公开号', 'ida', 'kind']], on = '专利公开号', how = 'left')
    # # 部分专利公开号的类型和app_pub_number的专利类型不符，但实际上是共用申请号
    # scientist1['专利公开号_fz'] = scientist1['专利公开号'].apply(lambda x: x.replace(' ','')[0:-1])
    # app_pub_number['专利公开号_fz'] = app_pub_number['专利公开号'].apply(lambda x: x[0:-1])
    # scientist1 = pd.merge(scientist1, app_pub_number[['专利公开号_fz', 'ida']], on='专利公开号_fz', how='left', suffixes=('','_0'))
    # scientist1['ida'].fillna(scientist1['ida_0'], inplace=True)
    # scientist1 = scientist1[scientist1['ida'].notnull()].copy()
    # scientist1 = scientist1[['ida', 'uniqueID', '姓名']]
    # scientist1.columns = ['ida', 'ID', 'Name']
    # scientist1.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    #
    # # 合并清洗后的scientist0,scientist1得到scientists
    # scientists = pd.concat([scientist0,scientist1], ignore_index=True)
    # scientists.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    # scientists.reset_index(inplace = True, drop = True)
    # scientists.to_csv('raw_data/scientists_nmclean.csv', index = False,encoding = 'utf-8')
    # # 删除不再需要的变量，释放内存
    # del app_pub_number
    # del scientist0
    # del scientist0_notmatch
    # del scientist0_match
    # del scientist0_notmatch_pnr
    # del scientist0_notmatch_pnr_n
    # del scientist1
    # gc.collect()
    #
    # # 此处是因为此代码清洗数据部分实际上是在命令行编写的，因此有再次导入scientists_nmclean的部分
    # # scientists = pd.read_csv('raw_data/scientists_nmclean.csv', encoding='utf-8')
    #
    # # 创建多层文件夹
    # files_per_folder = 100
    # folders_per_level = 100
    # base_dir = 'blocks_sample'
    # total_elements = len(scientists['Name'].unique())
    # depth = 0
    # while total_elements > 0:
    #     total_elements = total_elements // (files_per_folder * folders_per_level)
    #     depth += 1
    #
    # if os.path.exists(base_dir):
    #     shutil.rmtree(base_dir)
    # os.makedirs(base_dir, exist_ok=True)
    #
    # # 提取所有block文件路径，把需要的发明家对应的文件复制到blocks_sample中
    # block_files_path = show_files('blocks', [])
    # block_files = [os.path.splitext(os.path.basename(path))[0] for path in block_files_path]
    #
    # with ThreadPoolExecutor(6) as t:
    #     for index in tqdm(range(len(scientists['Name'].unique())), desc='save_blocks_sample', total=len(scientists['Name'].unique())):
    #         if replace_special_chars(scientists['Name'].unique()[index]) in block_files:
    #             t.submit(save_blocks_sample, index, block_files_path[block_files.index(replace_special_chars(scientists['Name'].unique()[index]))])
    # print('blocks_sample finished.')
    #
    # del block_files_path
    # del block_files
    # gc.collect()
    #
    # # 为训练集建立features
    # block_sample_path = show_files('blocks_sample', [])
    # with ThreadPoolExecutor(6) as t:
    #     for scientist in tqdm(block_sample_path, desc='scientists processing', total=len(block_sample_path)):
    #         t.submit(process_patents, scientist)
    #
    # print('features_sample finished.')
