"""
#!/usr/bin/env python
# _*_ coding:utf-8 -*_
@File :amap_geocode_inquiry.py
@author :Fan ZHANG
@Time :2023/11/06
@Descr:访问高德API，实现专利地址标准化
"""
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor
import time
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Ap\
                pleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Sa\
                fari/537.36"
}
key = '6809f51ea24cd02694e4639bb85260ea'
print(time.asctime())

# 这里列举待查询的文件清单，具体来说我分为30w条地址一个csv文件
list_file=['address_geo_re_re_inquiry']

# Define function to call Baidu Maps API for geocoding

#高德接口
def AutoNavi(location):
    print(location)
    url=f'https://restapi.amap.com/v3/geocode/geo?address={location}&output=XML&key={key}'
    try:
        rep = requests.get(url, headers=headers,timeout=3).text

        address='<formatted_address>(.*?)</formatted_address>'
        address = re.findall(address, rep)[0] if re.findall(address, rep) else None

        country = r'<country>(.*?)</country>'
        country = re.findall(country, rep)[0] if re.findall(country, rep) else None

        province = r'<province>(.*?)</province>'
        province = re.findall(province, rep)[0] if re.findall(province, rep) else None

        citycode = r'<citycode>(.*?)</citycode>'
        citycode = re.findall(citycode, rep)[0] if re.findall(citycode, rep) else None

        city = r'<city>(.*?)</city>'
        city = re.findall(city, rep)[0] if re.findall(city, rep) else None

        district = r'<district>(.*?)</district>'
        district = re.findall(district, rep)[0] if re.findall(district, rep) else None

        adcode = r'adcode>(.*?)</adcode>'
        adcode = re.findall(adcode, rep)[0] if re.findall(adcode, rep) else None

        street = r'<street>(.*?)</street>'
        street = re.findall(street, rep)[0] if re.findall(street, rep) else None

        number = r'<number>(.*?)</number>'
        number = re.findall(number, rep)[0] if re.findall(number, rep) else None

        Location = r'<location>(.*?)</location>'
        LonLat = re.findall(Location, rep)
        lon=LonLat[0].split(',')[0]  if LonLat else None
        lat=LonLat[0].split(',')[1]  if LonLat else None

        level = r'<level>(.*?)</level>'
        level = re.findall(level, rep)[0] if re.findall(level, rep) else None
        return [country,province,city,citycode,district,street,number,adcode,lon,lat,level,address]
    except:
        [None,None,None,None,None,None,None,None,None,None,None,None]

for file in list_file:
    # Read in table data using pandas
    table_data = pd.read_csv(file+'.csv', encoding='utf-8')

    # Use ThreadPoolExecutor to call geocode function for each address in table_data
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(AutoNavi, table_data['address']))

    # print(results)
    # Add geocoded location data to table_data
    table_data['国家'] = [result[0] if result is not None else None for result in results]
    table_data['省份'] = [result[1] if result is not None else None for result in results]
    table_data['城市'] = [result[2] if result is not None else None for result in results]
    table_data['城市编码'] = [result[3] if result is not None else None for result in results]
    table_data['地址所在的区'] = [result[4] if result is not None else None for result in results]
    table_data['街道'] = [result[5] if result is not None else None for result in results]
    table_data['门牌'] = [result[6] if result is not None else None for result in results]
    table_data['区域编码'] = [result[7] if result is not None else None for result in results]
    table_data['经度'] = [result[8] if result is not None else None for result in results]
    table_data['纬度'] = [result[9] if result is not None else None for result in results]
    table_data['匹配级别'] = [result[10] if result is not None else None for result in results]
    table_data['详细地址'] = [result[11] if result is not None else None for result in results]

    table_data.to_csv(file+'_result.csv', index=False)
print(time.asctime())
