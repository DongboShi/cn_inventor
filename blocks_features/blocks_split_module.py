import os
import gc
from tqdm import tqdm
import json
from get_features_json_threadpool import show_files
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import numpy as np
import time

def process_feature(folder_path, block_data, feature_name):
    # 处理单个特征并写入文件
    start = time.time()
    feature_data = ""
    for item in block_data:
        feature_data += f'{item[feature_name]}\n'

    with open(f'{folder_path}/{feature_name}.txt', mode='w', encoding='utf-8') as file:
        file.write(feature_data)
    end = time.time()
    print(f'process {folder_path}/{feature_name} spend {end - start}s.')

def process_block_file(b_path, features_need):
    try:
        folder_path = b_path.replace('blocks', 'blocks_total_split').replace('.json', '')
        # 检查文件是否存在
        start0 = time.time()
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

        files_exist = set(os.listdir(folder_path))
        if files_exist != set(features_need):
            with open(b_path, mode='r', encoding='utf-8') as f:
                block = json.load(f)
                inventor = list(block.keys())[0]
                block_data = block[inventor]
                print(f'input {b_path} spend {time.time() - start0}s.')

            # 为每个特征创建线程
            with ThreadPoolExecutor(15) as executor:
                for feature in features_need:
                    feature_name = feature.replace('.txt', '')
                    if f'{feature_name}.txt' not in files_exist:
                        executor.submit(process_feature, folder_path, block_data, feature_name)
    except Exception as e:
        print(f"Error: {e}")

def process_file_chunk(file_chunk, features_need):
    for b_file in file_chunk:
        process_block_file(b_file, features_need)