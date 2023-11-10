"""
#!/usr/bin/env python
# _*_ coding:utf-8 -*_
@File :amap_geocode_inquiry.py
@author :Fan ZHANG
@Time :2023/11/09
@Descr: 导入结果并匹配对应专利
"""

# 导入pandas模块
import pandas as pd
# 显示所有行
pd.set_option('display.max_rows', None)
# 显示所有列
pd.set_option('display.max_columns', None)


address = 'D:\\disam\\address.csv'
# 读取address.csv文件
df1 = pd.read_csv(address)
patents_num = len(df1)
print(f"There are {patents_num} patents.")

# 仅保留ida、country、postcode和address变量
df1 = df1[["ida", "country", "postcode", "address"]]

# 将country变量重命名为countrycode
df1 = df1.rename(columns={"country": "countrycode"})

# print(df1.head())

# 读取amap_geocode_total.csv文件
df2 = pd.read_csv("amap_geocode_total.csv")

df1["address"] = df1["address"].str.replace("#", "号")

# 根据address变量与address.csv文件中countrycode为CN的值匹配
# df = pd.merge(df1[df1["countrycode"] == "CN"], df2, on="address", how="left")
df = pd.merge(df1, df2, on="address", how="left")
print(len(df))

# print(df.head(10))

# 将匹配后“国家”为空指且address变量含有“台湾”,或者省份含有“台湾”的观测的countrycode变量改为TW
df.loc[(df["国家"].isnull()) & (df["address"].str.contains("台湾")), "countrycode"] = "TW"
df.loc[(df["国家"].isnull()) & (df["address"].str.contains("香港")), "countrycode"] = "HK"
df.loc[(df["国家"].isnull()) & (df["address"].str.contains("澳门")), "countrycode"] = "MO"
# 将变量“省份”含有“台湾”的观测的countrycode变量赋值为TW
df.loc[df["省份"].str.contains("台湾", na=False), "countrycode"] = "TW"
df.loc[df["省份"].str.contains("香港", na=False), "countrycode"] = "HK"
df.loc[df["省份"].str.contains("澳门", na=False), "countrycode"] = "MO"


patents_CN_num = len(df[df["countrycode"] == "CN"])
print(f"There are {patents_CN_num} patents locate in CN.")


'''
# 对于缺失的数据再做一次补充，主要缺失的原因还是#问题
# 统计变量countrycode为CN且变量国家为空值的观测
df = df[(df["countrycode"] == "CN") & (df["国家"].isnull())]
# 仅保留ida、countrycode、postcode和address变量
df = df[["ida", "countrycode", "postcode", "address"]]
# 导出结果为csv文件
df.to_csv("missing_address_jinghao.csv", index=False)
'''

# 处理海外地址数据
# 将countrycode为HK的观测的country赋值为中国香港
df.loc[df["countrycode"] == "HK", "国家"] = "中国香港"
df.loc[df["countrycode"] == "JP", "国家"] = "日本"
df.loc[df["countrycode"] == "KR", "国家"] = "韩国"
df.loc[df["countrycode"] == "US", "国家"] = "美国"
df.loc[df["countrycode"] == "CH", "国家"] = "瑞士"
df.loc[df["countrycode"] == "TW", "国家"] = "中国台湾"
df.loc[df["countrycode"] == "CA", "国家"] = "加拿大"
df.loc[df["countrycode"] == "DE", "国家"] = "德国"
df.loc[df["countrycode"] == "FR", "国家"] = "法国"
df.loc[df["countrycode"] == "AT", "国家"] = "奥地利"
df.loc[df["countrycode"] == "BS", "国家"] = "巴哈马"
df.loc[df["countrycode"] == "GB", "国家"] = "英国"
df.loc[df["countrycode"] == "IT", "国家"] = "意大利"
df.loc[df["countrycode"] == "IL", "国家"] = "以色列"
df.loc[df["countrycode"] == "VG", "国家"] = "英属维京群岛"
df.loc[df["countrycode"] == "FI", "国家"] = "芬兰"
df.loc[df["countrycode"] == "BR", "国家"] = "巴西"
df.loc[df["countrycode"] == "NL", "国家"] = "荷兰"
df.loc[df["countrycode"] == "AN", "国家"] = "荷属安的列斯群岛"
df.loc[df["countrycode"] == "DK", "国家"] = "丹麦"
df.loc[df["countrycode"] == "CU", "国家"] = "古巴"
df.loc[df["countrycode"] == "ZA", "国家"] = "南非"
df.loc[df["countrycode"] == "LI", "国家"] = "列支敦士登"
df.loc[df["countrycode"] == "AR", "国家"] = "阿根廷"
df.loc[df["countrycode"] == "UA", "国家"] = "乌克兰"
df.loc[df["countrycode"] == "MY", "国家"] = "马来西亚"
df.loc[df["countrycode"] == "SE", "国家"] = "瑞典"
df.loc[df["countrycode"] == "VE", "国家"] = "委内瑞拉"
df.loc[df["countrycode"] == "SG", "国家"] = "新加坡"
df.loc[df["countrycode"] == "PA", "国家"] = "巴拿马"
df.loc[df["countrycode"] == "CL", "国家"] = "智利"
df.loc[df["countrycode"] == "AU", "国家"] = "澳大利亚"
df.loc[df["countrycode"] == "BE", "国家"] = "比利时"
df.loc[df["countrycode"] == "AD", "国家"] = "安道尔"
df.loc[df["countrycode"] == "MO", "国家"] = "中国澳门"
df.loc[df["countrycode"] == "TH", "国家"] = "泰国"
df.loc[df["countrycode"] == "KY", "国家"] = "英属西印度群岛"
df.loc[df["countrycode"] == "IN", "国家"] = "印度"
df.loc[df["countrycode"] == "CO", "国家"] = "哥伦比亚"
df.loc[df["countrycode"] == "ES", "国家"] = "西班牙"
df.loc[df["countrycode"] == "X", "国家"] = "不公告地址"
df.loc[df["countrycode"] == "RU", "国家"] = "俄罗斯"
df.loc[df["countrycode"] == "PL", "国家"] = "波兰"
df.loc[df["countrycode"] == "MC", "国家"] = "摩纳哥"
df.loc[df["countrycode"] == "NO", "国家"] = "挪威"
df.loc[df["countrycode"] == "IE", "国家"] = "爱尔兰"
df.loc[df["countrycode"] == "CZ", "国家"] = "捷克"
df.loc[df["countrycode"] == "PH", "国家"] = "菲律宾"
df.loc[df["countrycode"] == "CY", "国家"] = "塞浦路斯"
df.loc[df["countrycode"] == "MX", "国家"] = "墨西哥"
df.loc[df["countrycode"] == "LU", "国家"] = "卢森堡"
df.loc[df["countrycode"] == "NZ", "国家"] = "新西兰"
df.loc[df["countrycode"] == "EE", "国家"] = "爱沙尼亚"
df.loc[df["countrycode"] == "PT", "国家"] = "葡萄牙"
df.loc[df["countrycode"] == "BG", "国家"] = "保加利亚"
df.loc[df["countrycode"] == "RO", "国家"] = "罗马尼亚"
df.loc[df["countrycode"] == "BH", "国家"] = "巴林"
df.loc[df["countrycode"] == "GR", "国家"] = "希腊"
df.loc[df["countrycode"] == "TR", "国家"] = "土耳其"
df.loc[df["countrycode"] == "IS", "国家"] = "冰岛"
df.loc[df["countrycode"] == "SI", "国家"] = "斯洛文尼亚"
df.loc[df["countrycode"] == "HU", "国家"] = "匈牙利"
df.loc[df["countrycode"] == "BM", "国家"] = "百慕大"
df.loc[df["countrycode"] == "MT", "国家"] = "马耳他"
df.loc[df["countrycode"] == "HR", "国家"] = "克罗地亚"
df.loc[df["countrycode"] == "UZ", "国家"] = "乌兹别克斯坦"
df.loc[df["countrycode"] == "AE", "国家"] = "阿拉伯联合酋长国"
df.loc[df["countrycode"] == "SA", "国家"] = "沙特阿拉伯"
df.loc[df["countrycode"] == "UY", "国家"] = "乌拉圭"
df.loc[df["countrycode"] == "SK", "国家"] = "斯洛伐克"
df.loc[df["countrycode"] == "BB", "国家"] = "巴巴多斯"
df.loc[df["countrycode"] == "GI", "国家"] = "直布罗陀"
df.loc[df["countrycode"] == "TC", "国家"] = "英属特克斯和凯科斯群岛"
df.loc[df["countrycode"] == "CR", "国家"] = "哥斯达黎加"
df.loc[df["countrycode"] == "MG", "国家"] = "马达加斯加"
df.loc[df["countrycode"] == "KP", "国家"] = "朝鲜"
df.loc[df["countrycode"] == "IQ", "国家"] = "伊拉克"
df.loc[df["countrycode"] == "KZ", "国家"] = "哈萨克斯坦"
df.loc[df["countrycode"] == "JE", "国家"] = "英国泽西海峡群岛"
df.loc[df["countrycode"] == "MU", "国家"] = "毛里求斯"
df.loc[df["countrycode"] == "TN", "国家"] = "突尼斯"
df.loc[df["countrycode"] == "SV", "国家"] = "萨尔瓦多"
df.loc[df["countrycode"] == "CK", "国家"] = "库克群岛"
df.loc[df["countrycode"] == "BZ", "国家"] = "伯利兹"
df.loc[df["countrycode"] == "SC", "国家"] = "塞舌尔"
df.loc[df["countrycode"] == "BY", "国家"] = "白俄罗斯"
df.loc[df["countrycode"] == "RS", "国家"] = "南斯拉夫"
df.loc[df["countrycode"] == "DO", "国家"] = "多米尼加"
df.loc[df["countrycode"] == "SM", "国家"] = "圣马力诺"
df.loc[df["countrycode"] == "TT", "国家"] = "特立尼达和多巴哥"
df.loc[df["countrycode"] == "ML", "国家"] = "菲律宾"
df.loc[df["countrycode"] == "LV", "国家"] = "拉脱维亚"
df.loc[df["countrycode"] == "VU", "国家"] = "瓦努阿图"
df.loc[df["countrycode"] == "IM", "国家"] = "马恩岛"
df.loc[df["countrycode"] == "ZW", "国家"] = "津巴布韦"
df.loc[df["countrycode"] == "SY", "国家"] = "叙利亚"
df.loc[df["countrycode"] == "EG", "国家"] = "埃及"
df.loc[df["countrycode"] == "KN", "国家"] = "尼维斯岛"
df.loc[df["countrycode"] == "JO", "国家"] = "约旦"
df.loc[df["countrycode"] == "MA", "国家"] = "摩洛哥"
df.loc[df["countrycode"] == "DZ", "国家"] = "阿尔及利亚"
df.loc[df["countrycode"] == "WS", "国家"] = "萨摩亚"
df.loc[df["countrycode"] == "EC", "国家"] = "厄瓜多尔"
df.loc[df["countrycode"] == "LB", "国家"] = "黎巴嫩"
df.loc[df["countrycode"] == "KW", "国家"] = "科威特"
df.loc[df["countrycode"] == "CM", "国家"] = "喀麦隆"
df.loc[df["countrycode"] == "KG", "国家"] = "吉尔吉斯斯坦"
df.loc[df["countrycode"] == "AW", "国家"] = "阿鲁巴"
df.loc[df["countrycode"] == "VC", "国家"] = "圣文森特和格林纳丁斯"
df.loc[df["countrycode"] == "GE", "国家"] = "格鲁吉亚"
df.loc[df["countrycode"] == "LK", "国家"] = "斯里兰卡"
df.loc[df["countrycode"] == "LT", "国家"] = "立陶宛"
df.loc[df["countrycode"] == "BN", "国家"] = "文莱"
df.loc[df["countrycode"] == "IR", "国家"] = "伊朗"
df.loc[df["countrycode"] == "CI", "国家"] = "科特迪瓦"
df.loc[df["countrycode"] == "AG", "国家"] = "安提瓜"
df.loc[df["countrycode"] == "OM", "国家"] = "阿曼"
df.loc[df["countrycode"] == "AZ", "国家"] = "阿塞拜疆"
df.loc[df["countrycode"] == "VN", "国家"] = "越南"
df.loc[df["countrycode"] == "AM", "国家"] = "亚美尼亚"
df.loc[df["countrycode"] == "AI", "国家"] = "安圭拉"
df.loc[df["countrycode"] == "BI", "国家"] = "布隆迪"
df.loc[df["countrycode"] == "PK", "国家"] = "巴基斯坦"
df.loc[df["countrycode"] == "BO", "国家"] = "玻利维亚"
df.loc[df["countrycode"] == "GD", "国家"] = "圣文森特和格林纳丁斯"
df.loc[df["countrycode"] == "GT", "国家"] = "危地马拉"
df.loc[df["countrycode"] == "NG", "国家"] = "尼日利亚"
df.loc[df["countrycode"] == "GG", "国家"] = "英属根西岛"
df.loc[df["countrycode"] == "MD", "国家"] = "摩尔多瓦"
df.loc[df["countrycode"] == "MN", "国家"] = "蒙古"
df.loc[df["countrycode"] == "PE", "国家"] = "秘鲁"
df.loc[df["countrycode"] == "GH", "国家"] = "瑞典"
df.loc[df["countrycode"] == "KE", "国家"] = "肯尼亚"
df.loc[df["countrycode"] == "TD", "国家"] = "乍得"
df.loc[df["countrycode"] == "QA", "国家"] = "卡塔尔"
df.loc[df["countrycode"] == "列支敦士登", "国家"] = "列支敦士登"
df.loc[df["countrycode"] == "巴巴多斯", "国家"] = "巴巴多斯"
df.loc[df["countrycode"] == "MK", "国家"] = "北马其顿共和国"
df.loc[df["countrycode"] == "JM", "国家"] = "牙买加"
df.loc[df["countrycode"] == "BD", "国家"] = "孟加拉国"
df.loc[df["countrycode"] == "ID", "国家"] = "印尼"
df.loc[df["countrycode"] == "MH", "国家"] = "马绍尔群岛"
df.loc[df["countrycode"] == "ER", "国家"] = "厄立特里亚"
df.loc[df["countrycode"] == "AL", "国家"] = "阿尔巴尼亚"
df.loc[df["countrycode"] == "PY", "国家"] = "巴拉圭"
df.loc[df["countrycode"] == "SD", "国家"] = "苏丹"
df.loc[df["countrycode"] == "ZM", "国家"] = "赞比亚"
df.loc[df["countrycode"] == "CW", "国家"] = "库拉索"
df.loc[df["countrycode"] == "KH", "国家"] = "柬埔寨"
df.loc[df["countrycode"] == "LR", "国家"] = "利比里亚"
df.loc[df["countrycode"] == "AO", "国家"] = "安哥拉"
df.loc[df["countrycode"] == "XP", "国家"] = "德国"
df.loc[df["countrycode"] == "LC", "国家"] = "圣卢西亚"
df.loc[df["countrycode"] == "ME", "国家"] = "黑山"
df.loc[df["countrycode"] == "TM", "国家"] = "土库曼斯坦"
df.loc[df["countrycode"] == "CD", "国家"] = "刚果民主共和国"
df.loc[df["countrycode"] == "CF", "国家"] = "中非共和国"
df.loc[df["countrycode"] == "FJ", "国家"] = "斐济"
df.loc[df["countrycode"] == "SU", "国家"] = "俄罗斯"
df.loc[df["countrycode"] == "YU", "国家"] = "南斯拉夫"
df.loc[df["countrycode"] == "SZ", "国家"] = "斯威士兰"
df.loc[df["countrycode"] == "SN", "国家"] = "塞内加尔"
df.loc[df["countrycode"] == "GN", "国家"] = "几内亚"
df.loc[df["countrycode"] == "NE", "国家"] = "尼日尔尼亚美"
df.loc[df["countrycode"] == "BA", "国家"] = "波斯尼亚和黑塞哥维那"
df.loc[df["countrycode"] == "LY", "国家"] = "利比亚"
df.loc[df["countrycode"] == "NP", "国家"] = "尼泊尔"
df.loc[df["countrycode"] == "LA", "国家"] = "老挝"
df.loc[df["countrycode"] == "TJ", "国家"] = "塔吉克斯坦"
df.loc[df["countrycode"] == "PS", "国家"] = "巴勒斯坦"
df.loc[df["countrycode"] == "开曼群岛", "国家"] = "开曼群岛"
df.loc[df["countrycode"] == "塞舌尔", "国家"] = "塞舌尔"
df.loc[df["countrycode"] == "百慕大群岛", "国家"] = "百慕大群岛"
df.loc[df["countrycode"] == "安提瓜和巴布达", "国家"] = "安提瓜和巴布达"
df.loc[df["countrycode"] == "英属维尔京群岛", "国家"] = "英属维尔京群岛"
df.loc[df["countrycode"] == "伯利兹", "国家"] = "伯利兹"
df.loc[df["countrycode"] == "圣基茨和尼维斯", "国家"] = "圣基茨和尼维斯"
df.loc[df["countrycode"] == "BJ", "国家"] = "贝宁"
df.loc[df["countrycode"] == "CG", "国家"] = "刚果民主共和国"
df.loc[df["countrycode"] == "PR", "国家"] = "波多黎各"

# 导出结果为csv文件
df.to_csv("formatted_address_1110.csv", index=False)

# 统计变量countrycode为CN且变量国家为空值的观测的个数
missing_count_CN = df[(df["countrycode"] == "CN") & (df["国家"].isnull())].shape[0]
missing_count_total = df["国家"].isnull().sum()
print(f"There are {missing_count_CN} missing Chinese address.")
print(f"There are {missing_count_total} missing address in total.")



# 导出中国地址缺失值
# 仅保留变量countrycode为CN且变量国家为空值的观测
df[df["国家"].isnull()].to_csv("missing_address_total.csv", index=False)







