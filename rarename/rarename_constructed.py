#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :rarename_constructed.py
# @Author    :FanZhang

# 基于indv.txt文件构造稀有名数据集

# 导入csv和pandas模块
import csv
import pandas as pd
import time
# 显示所有行
pd.set_option('display.max_rows', None)
# 显示所有列
pd.set_option('display.max_columns', None)


print(time.asctime())

# 导入indv数据集
indv = 'D:\\disam\\indv.txt'
df = pd.read_csv(indv, sep='\t', header=None, low_memory=False)

# 将第二列命名为name，使用rename函数，指定axis=1表示列
df.columns = names = ['id', 'name']
# print(df.head())

total_names = len(df)
print(f'there are {total_names} names in indv.txt in total.')

# 进行预处理：仅保留中国姓名
# 定义一个函数，判断一个姓名是否是中国人姓名
def is_chinese_name(name):
    # 假设中国人姓名只包含中文字符
    if not isinstance(name, str):
        return False # 如果name不是字符串，直接返回False
    for char in name:
        if not ("\u4e00" <= char <= "\u9fff"):
            return False
    return True

# 筛选出inventor变量值为中国人姓名的观测
df = df[df["name"].apply(is_chinese_name)]

# 剔除长度大于4的姓名
# 计算name变量的字符串长度，并过滤出长度大于4的观测
# 定义一个自定义的函数，用于返回字符串的长度
def get_length(s):
    return len(s)

# 对inventor变量的值应用自定义的函数，返回字符串长度
df['length'] = df['name'].apply(get_length)

# 对inventor变量的值按照字符串长度进行筛选，只保留长度小于5的变量
df = df.query('length < 5')

# print(df.head())

cn_names_num = len(df)
print(f"there are {cn_names_num} Chinese names.")


# 构建复姓库
complex_surnames = ['欧阳', '太史', '端木', '上官', '司马', '东方', '独孤', '万俟', '闻人',\
                    '夏侯', '诸葛', '尉迟', '公羊', '赫连', '澹台', '皇甫', '宗政', '濮阳', '公冶',\
                    '太叔', '申屠', '公孙', '慕容', '仲孙', '钟离', '长孙', '宇文', '城池', '司徒',\
                    '鲜于', '司空', '汝嫣', '闾丘', '子车', '亓官', '司寇', '巫马', '公西', '颛孙',\
                    '壤驷', '公良', '漆雕', '乐正', '宰父', '谷梁', '拓跋', '夹谷', '轩辕', '令狐',\
                    '段干', '百里', '呼延', '东郭', '南门', '羊舌', '微生', '公户', '公玉', '公仪',\
                    '梁丘', '公仲', '公上', '公门', '公山', '公坚', '左丘', '公伯', '西门', '公祖',\
                    '第五', '公乘', '贯丘', '公皙', '南荣', '东里', '东宫', '仲长', '子书', '子桑',\
                    '即墨', '达奚', '褚师', '东门', '南宫', '淳于', '单于', '黄辰', '乌孙',\
                    '完颜', '富察', '费莫', '锺离', '东欧', '聂晁', '空曾', '相查', '荔菲', '辗迟',\
                    '归海', '有琴', '章佳', '那拉', '纳喇', '乌雅', '范姜', '碧鲁', '张廖', '张简',\
                    '图门', '公叔']

# 创建变量firstname和lastname
firstname = []
lastname = []

# 遍历name变量
for name in df['name']:
    # 若name变量只有两个字符，则第一个为firstname，第二个为lastname
    if len(name) == 2:
        firstname.append(name[0])
        lastname.append(name[1])
    # 若name变量有两个以上字符
    else:
        # 判断前两个字符是否在复姓库中
        if name[:2] in complex_surnames:
            # 若在则前两个字符为firstname，剩下的为lastname
            firstname.append(name[:2])
            lastname.append(name[2:])
        else:
            # 若不在，则第一个字符为firstname，剩下的为lastname
            firstname.append(name[0])
            lastname.append(name[1:])

# 将firstname和lastname添加到数据框中
df['firstname'] = firstname
df['lastname'] = lastname

# 计算firstname中各个值出现的概率
firstname_prob = df["firstname"].value_counts(normalize=True)

# 计算lastname中各个值出现的概率
lastname_prob = df["lastname"].value_counts(normalize=True)

# 计算name_prob为firstname_prob与lastname_prob相乘
# name_prob = df.apply(lambda x: firstname_prob[x["firstname"]] * lastname_prob[x["lastname"]], axis=1)

# 将两个新生成的变量添加到数据框中，使用join方法
df = df.join(firstname_prob, on="firstname", rsuffix="_prob")
df = df.join(lastname_prob, on="lastname", rsuffix="_prob")

# 删除不需要的变量
df = df.drop(["id", "length"], axis=1)

print(df.head(10))

df.to_csv('indv_name_info.csv', index=False)


print(time.asctime())
