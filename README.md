# cn_inventor
disambiguate inventors of Chinese patents

## 技术说明

一个专利申请号可能会对应多个公开号，因此，专利的唯一id使用专利申请号

## 相关数据说明

1. appln_nr_cn.csv

专利申请号-公开号的对应关系，以逗号分隔文件

|变量|说明|
|-------------------|---------------|
|appln_id           |专利申请号|
|publn_nr           |公开号，注意一个申请号可能对应多个公开号|
|publn_auth         |专利授权机构CN|
|publn_nr_original|专利原始公开号"U","Y","S"表示实用新型与发明专利|
|publn_kind|专利类型|
|publn_first_grant|是否首次授权|
|docdb_family_id|专利族编号，这个号码一致的表示同一个专利，可以用于专利号去重复|

2. cn_ipc.txt
   
以|分隔文件，专利对应的ipc编号，该文件没有表头，第一列为专利申请号（此处专利申请号与表1中有些差异，注意去除连字符以及尾巴上的字母），第二列为专利的完整ipc编号

3. cn_title.txt

以|分隔文件，专利标题，该文件没有表头，第一列为专利申请号，第二列为专利标题

4. inventor.csv

逗号分隔文件，专利的发明人，这是我们要计算的对象，要根据这部分来建立block

|变量|说明|
|-------------------|---------------|
|ida           |专利申请号|
|inventor           |发明人|
|inventor_seq         |发明人顺序|

5. address.csv

逗号分隔文件，专利对应的地址，有部分地址缺失的是经纬度信息

|变量|说明|
|-------------------|---------------|
|ida           |专利申请号|
|country           |CN|
|province         |省份|
|city|城市|
|county|县区|
|address|具体地址|
|state_code|可忽略|

6. address_geocode.txt

制表符分隔文件，地址的高德坐标信息（2018年前专利的地址，因此会有遗漏）
|变量|说明|
|-------------------|---------------|
| formatted_address | 地址          | 
| province          | 省          |
| citycode          | 城市代码          |
| city              | 城市          |
| district          | 区域          |
| adcode            | 区域代码          |
| location          | 高德位置          |
| level             | 地址级别          |
| lat               | 维度        |
| lng               | 经度     |
| _id               | 忽略     |
| addr              | 解析后的地址 | 

7. applicant.csv

逗号分隔文件，专利权人表

|变量|说明|
|-------------------|---------------|
|ida           |专利申请号|
|applicant           |专利权人|
|applicant_seq         |专利权人顺序|
|org_code|组织机构代码|
|applicant_type|专利权人类型，1-个人 2-企业 3-大学 4-事业单位|

8.scientist.csv

科学家专利申请列表，阳性准确集样本；scientists2.xlsx加了几十个科学家

9. name_dist.csv
基于10万个科学家的记录信息

10.app_pub_number.txt |分割

|变量|说明|
|-------------------|---------------|
|pnr|专利公开号|
|ida           |专利申请号|
|country           |国家代码|
|kind         |类型|
|pct|pct号|
|fmlyid|专利族号|

从这表里面筛出来中国的专利，注意ida和pnr有“-”要删除一下。然后这个没有表头，需要读入的时候自己加一下。

11. cn_e_cite_all.csv 专利间的引用关系

使用citing_ida（施引专利的申请号）和cited_ida（被引专利的申请号）

## 技术路线

1. 公安局法人账号（史冬波）

山西中京翼隆商贸有限公司
91140400MA0HMFK35U
密码:Lp123456

已经放入科学家名字分布信息在name_dist.csv

2. 高德解析缺失地址（张繁）

高德的api账号为，之前使用的参考代码放在文件夹gaodeapi里面，忽略其中的sql相关部分代码（这部分代码是因为之前的专利储存在sql里面）

3. 使用科学家名字先筛选发明人查询的名单

4. 计算已经可以计算的feature

5. 支线任务，从google patents获取所有专利的description的数据（岩钧）

具体来说，就是通过专利号和谷歌专利的网址页规律，直接进入谷歌专利网页，直接从静态网页中得到相关内容即可。

包括专利的description和引用信息，专利引用解析Patent Citations和Family Cites Families这两个表。

## 1106进度

1. 岩钧已完成谷歌专利获取与解析的脚本；

2. 张繁（待补充）
