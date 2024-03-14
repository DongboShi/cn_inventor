import os
from time import time
from concurrent.futures import ThreadPoolExecutor, as_completed


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
        for folder in folders:
            cur_path = os.path.join(home, folder)
            file_list = show_folders(cur_path)
            if file_list:
                show_folders(cur_path)
            else:
                all_folders.append(os.path.join(home, folder))
    return all_folders


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


def process_entire_name(entire_name, rarename_dict):
    start = time()
    block_files = show_files(rarename_dict[entire_name], [])
    temp_data = {key: [] for key in blocks_lst}
    with ThreadPoolExecutor(max_workers=12) as tp:
        # 提交所有文件处理任务，并保留futures以保持顺序
        futures = [tp.submit(process_file, file) for file in block_files]
        # 按提交顺序获取future结果
        for future in futures:
            try:
                # 尝试解包future的结果
                block_name, block_values = future.result()
                temp_data[block_name].extend(block_values)
            except ValueError as e:
                print(f"Error unpacking future result: {e}")
    temp_data['scientist_name'].extend([entire_name] * len(block_values))
    print(f'{entire_name} finished. Cost {time() - start}s')
    return temp_data


def merge_results(blocks_total_data, results, blocks_lst):
    for key in blocks_lst:
        for result in results:
            blocks_total_data[key].extend(result[key])


def output_file(file_path, key, blocks_total_data):
    with open(os.path.join(file_path, f'{key}.txt'), mode='w', encoding='utf-8') as f:
        for row in blocks_total_data[key]:
            f.write(f'{row}\n')


def surname_blocks(surname, surname_block_paths):
    blocks_total_data = {key: [] for key in blocks_lst}
    start_surname = time()
    with ThreadPoolExecutor(max_workers=12) as executor:
        # 提交任务
        futures = [executor.submit(process_entire_name, entire_name, rarename_dict) for entire_name in
                   surname_dict[surname]]
        # 按照任务完成的顺序收集结果
        results = []
        for future in as_completed(futures):
            results.append(future.result())

    # 合并结果，保持顺序
    merge_results(blocks_total_data, results, blocks_lst)
    print(f'{surname} finished. Cost {time() - start_surname}s')
    file_path = surname_block_paths[surname]
    os.makedirs(file_path, exist_ok=True)
    with ThreadPoolExecutor(max_workers=12) as t:
        for key in blocks_lst:
            t.submit(output_file, file_path, key, blocks_total_data)
    print(f'{surname} outputs. Cost {time() - start_surname}s')


def create_files(surname_dict, root_path, surname_block_paths, per_folder=100):
    def make_path(path, idx, is_file=False):
        return os.path.join(path, f"{idx // per_folder}" if is_file else f"{idx // per_folder}")

    os.makedirs(root_path, exist_ok=True)
    folder_paths = {}
    for i, surname in enumerate(surname_dict):
        folder_index = i // (per_folder ** 2)
        if folder_index not in folder_paths:
            folder_path = os.path.join(root_path, f"{folder_index}")
            os.makedirs(folder_path, exist_ok=True)
            folder_paths[folder_index] = folder_path

        file_folder_path = make_path(folder_paths[folder_index], i, is_file=True)
        if not os.path.exists(file_folder_path):
            os.makedirs(file_folder_path, exist_ok=True)

        file_path = os.path.join(file_folder_path, f"{surname}")
        surname_block_paths[surname] = file_path


blocks_lst = {'latitude', 'patent_title', 'country', 'inventor_lst', 'citing_lst', 'scientist_name',
              'detailed_address', 'cited_lst', 'road', 'ipc_class', 'applicants_lst',
              'longitude', 'province', 'ida', 'district', 'city', 'ipc_group', 'housenumber', 'app_first'}


if __name__ == '__main__':
    rarename_lst = show_folders('blocks_split')
    rarename_dict = {}
    for file in rarename_lst:
        rarename_dict[os.path.basename(file)] = file

    japanese_surname = ['佐藤', '伊藤']
    japanese_surname_d = set([i[0:2] for i in rarename_lst if i[0] == '大'])
    japanese_surname.extend(japanese_surname_d)
    compound_surname = ['欧阳', '太史', '端木', '上官', '司马', '东方', '独孤', '万俟', '闻人',
                        '夏侯', '诸葛', '尉迟', '公羊', '赫连', '澹台', '皇甫', '宗政', '濮阳',
                        '公冶', '太叔', '申屠', '公孙', '慕容', '仲孙', '钟离', '长孙', '宇文',
                        '城池', '司徒', '鲜于', '司空', '汝嫣', '闾丘', '子车', '亓官', '司寇',
                        '巫马', '公西', '颛孙', '壤驷', '公良', '漆雕', '乐正', '宰父', '谷梁',
                        '拓跋', '夹谷', '轩辕', '令狐', '段干', '百里', '呼延', '东郭', '南门',
                        '羊舌', '微生', '公户', '公玉', '公仪', '梁丘', '公仲', '公上', '公门',
                        '公山', '公坚', '左丘', '公伯', '西门', '公祖', '第五', '公乘', '贯丘',
                        '公皙', '南荣', '东里', '东宫', '仲长', '子书', '子桑', '即墨', '达奚',
                        '褚师', '东门', '南宫', '淳于', '单于', '黄辰', '乌孙', '完颜', '富察',
                        '费莫', '锺离', '东欧', '聂晁', '空曾', '相查', '荔菲', '辗迟', '归海',
                        '有琴', '章佳', '那拉', '纳喇', '乌雅', '范姜', '碧鲁', '张廖', '张简', '图门', '公叔']

    surname_lst = []
    for i in rarename_dict:
        if (i[0:2] in japanese_surname) or (i[0:2] in compound_surname):
            surname_lst.append(i[0:2])
        else:
            surname_lst.append(i[0])
    surname_lst = set(surname_lst)
    surname_dict = {}
    for i in surname_lst:
        surname_dict[i] = []

    for i in rarename_dict:
        if (i[0:2] in japanese_surname) or (i[0:2] in compound_surname):
            surname_dict[i[0:2]].append(i)
        else:
            surname_dict[i[0]].append(i)

    surname_block_paths = {}
    create_files(surname_dict, 'rarename_blocks', surname_block_paths, per_folder=100)

    with ThreadPoolExecutor(max_workers=12) as t:
        for surname in surname_dict:
            t.submit(surname_blocks, surname, surname_block_paths)
