import os
from tqdm import tqdm
import json
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import numpy as np
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

def main():
    block_files_path = show_files('blocks', [])
    # 读取特征需求
    with open('features_need.txt', mode='r', encoding='utf-8') as f:
        features_need = [line.strip() + ".txt" for line in f.readlines()]
    # 分割文件列表
    num_processors = 30
    split_block_files = np.array_split(block_files_path, num_processors)
    with ProcessPoolExecutor(max_workers=num_processors) as executor:
        for file_chunk in split_block_files:
            executor.submit(process_file_chunk, file_chunk, features_need)

if __name__ == '__main__':
    main()