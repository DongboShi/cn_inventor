"""
#!/usr/bin/env python
# _*_ coding:utf-8 -*_
@File :amap_geocode_inquiry.py
@author :Fan ZHANG
@Time :2023/11/09
@Descr: 整合高德API访问结果
"""

# 导入pandas库
import pandas as pd

# 导入address1、address2、address3文件，假设是以逗号分隔的csv文件
df1 = pd.read_csv('address_1_result.csv')
df2 = pd.read_csv('address_2_result.csv')
df3 = pd.read_csv('address_3_result.csv')
df4 = pd.read_csv('address_4_result.csv')
df_re = pd.read_csv('address_re_inquiry_result.csv')
df_re_re = pd.read_csv('address_re_re_inquiry_result.csv')

# 将它们纵向拼接起来
df = pd.concat([df1, df2, df3, df4, df_re, df_re_re], ignore_index=True)

# 删除ida变量
df = df.drop('ida', axis=1)

print(df.head())
print(len(df))
# df = df[~(df["国家"].isnull() & df["address"].str.contains("#"))]
df = df[~df['address'].str.contains('#')]
print(len(df))

# 导入addressgeo1、addressgeo2、addressgeo3文件，假设是以逗号分隔的csv文件
df_geo_1 = pd.read_csv('address_geo_1_result.csv')
df_geo_2 = pd.read_csv('address_geo_2_result.csv')
df_geo_3 = pd.read_csv('address_geo_3_result.csv')
df_geo_4 = pd.read_csv('address_geo_4_result.csv')
df_geo_re = pd.read_csv('address_geo_re_re_inquiry_result.csv')

# 将它们纵向拼接起来
df_geo = pd.concat([df_geo_1, df_geo_2, df_geo_3, df_geo_4, df_geo_re], ignore_index=True)

print(df_geo.head())
print(len(df_geo))
# df_geo = df_geo[~(df_geo["国家"].isnull() & df_geo["address"].str.contains("#"))]
df_geo = df_geo[~df_geo['address'].str.contains('#')]
print(len(df_geo))


# 将两个拼接结果再纵向拼接
df = pd.concat([df, df_geo], ignore_index=True)

# 根据address变量去除重复值，保留country变量非空的最后一个值
df = df.sort_values(by='国家', na_position='first').drop_duplicates(subset='address', keep='last')

amap_geocode_num = len(df)
print(f"there are {amap_geocode_num} amap geocode collected.")

# 导出结果，假设文件名为output.csv
df.to_csv('amap_geocode_total.csv', index=False)













