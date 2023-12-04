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

12. formatted_address_1110.csv 标准的地址信息

- ##### 原始地址数据来源与标准地址数据来源

  原始地址数据全部来自address.csv文件，由于缺少“街道”和“门牌号”两个关键变量，因此没有使用address_geocode.txt的数据，标准地址数据全部来自高德地理编码API。我们将address.csv中以完整字符串形式记录的专利地址信息，拼接入HTTP中请求URL，接收HTTP请求返回的如下数据：

  | 参数名       | 参数名_ENG        | 含义         | 规则说明                                     |
  | ------------ | ----------------- | ------------ | -------------------------------------------- |
  | ida          | ida               | 专利申请号   |                                              |
  | countrycode  | countrycode       | 国家编码     | 仅收集中国大陆的地址，即CN，不包括TW、HK、MO |
  | postcode     | postcode          | 邮政编码     |                                              |
  | address      | address           | 原始地址信息 |                                              |
  | 国家         | country           |              |                                              |
  | 省份         | province          |              | 中国的四大直辖市也算作省级单位。             |
  | 城市         | city              |              |                                              |
  | 城市编码     | citycode          |              |                                              |
  | 地址所在的区 | district          |              |                                              |
  | 街道         | street            |              |                                              |
  | 门牌         | number            |              |                                              |
  | 区域编码     | adcode            |              |                                              |
  | 经度         | lon               |              |                                              |
  | 纬度         | lat               |              |                                              |
  | 匹配级别     | level             | 匹配精度     | 62.5%门牌号、15.3%兴趣点、7.0%道路、5.4%村庄 |
  | 详细地址     | formatted_address | 标准地址信息 |                                              |

  通过高德地图API，共计标准化了13,454,909条中国大陆的地址信息。

- ##### 海外地址特别处理

  对于海外的地址信息，即中国香港、中国澳门和中国台湾，以及其他国家的地址信息，则根据address.csv中“country”变量记录的国家/地区编码，进行了一个级别的地址信息划分，如分为日本、美国、中国台湾等。

  最终，两个处理方式加起来共计完成了16,258,557项专利的地址标准化工作。

- ##### 过程细节

  - 更正了少量的地区编码

  ​	address.csv中将少数（两万余条）中国香港、中国澳门和中国台湾的地址错误标记为中国大陆的编码。在访问高德地图API之前，预先对这批数据进行了预处理，更正了地区编码。

  - 特殊字符预处理

  ​	特殊字符的出现会影响url的判断，这也将导致空值的出现，需要提前对原始数据进行预处理。专利的地址信息中常见的有井号“#”和顿号“、”。我们将原始地址信息中的“#”替换为字符“号”再访问高德地图API，便能得到正确的结果。

13. 稀有姓名数据集1&2

原始姓名数据集均来自inventor.csv，还用到了indv.txt和科学家姓名分布数据name_dist.csv。inventor.csv中包含5477w条专利-发明人记录，indv.txt包含4102w位股东的姓名信息并且均包含唯一的标识符，name_dist.csv包含了100306位科学家拥有的85153个不同姓名的分布数据。后两个数据集主要用于排除非稀有姓名和计算姓氏/名字的分布情况。

- ### rarename_list_xmzj_1123.csv——姓名之家网站查询结果

​	姓名集1的搜集分为两大步骤——筛选出最可能稀有的发明人姓名，再在“姓名之家”网站查询重名人数

- 整理待查询的姓名清单

  1. 原始数据为inventor.csv中的第一发明人的姓名
  2. 剔除无歧义的姓名
  3. 去除重复值
  4. 剔除24w个外国人姓名（含特殊符号，或者长度大于4）
  5. 利用name_dist.csv和indv.txt，分别剔除0.7w和63w个非稀有姓名
  6. 根据indv.txt数据集，选取上一步中最稀有的24w个姓名
     - 我们分为姓氏和名字两部分，分别计算各自的稀有度，再求乘积。
     - 姓氏方面，根据《中国姓氏大全》和维基百科的中国姓氏排名等来源，我们构建了中国复姓库，用于识别双字复姓。仅取了两字名、三字名和部分四字名，四字名的有限选取是因为大量日本、韩国等国家的人名也包含在待查询的姓名集当中，这些名字在姓名网上查询的效率低、质量差，因此剔除而仅选取了能被复姓库识别的四字名。
     - 名字方面，此处没有进行拆字处理，而将名字作为一个整体进行统计。值得一提的是，无论是发明家还是股东的姓名，都有约5700个汉字被不同程度的使用了。因此，双字名将出现非常多可能的组合，indv.txt数据集中名字的分布十分稀疏，inventor.csv还有很多（几十万）没有出现过的名字。从而，对稀有姓名的定义十分粗糙，待查询的姓名都是名字在indv.txt中仅出现一次或没出现过的姓名。

- 爬取“姓名之家”重名查询，选取查询结果为“未查询到”的姓名为稀有姓名，共计93,389条

  - 数据来源选取过程

    中国公民的姓名分布数据，属于非公开的数据，稀有姓名数据的获取十分困难。目前，中国已有官方开发的“公安部互联网+政务服务平台”，其中的“查询同名人数”功能调用自公安部官方户籍数据，是最为精确的查询结果。但是这个网站有十分严格的每日查询次数限制，无论是个人用户，还是法人用户，都只能进行每天10次的查询。我们需要查询的姓名数量大约在30w左右，因而不得不放弃这个网站。国家级的网站行不通，我们还考虑了结合所有省级重名查询平台，拼凑出全国的数据。省级重名查询网站的数据收集同样困难，比如河南省也设置了每天10次的查询限制，江苏省的限制则在约2万次。更重要的是，有约十个省份没有开发自己的重名查询平台，或是不再维护而无法使用。综上所述，我们不得不选择信任民营的重名查询网站，即使它说明了“本页面的结果来自于近年网络数据的统计及估算,非真实户籍人口数据，重名或多或少”。最终，我们选取了“姓名之家”网站进行数据爬取。

  - 查询结果分析与稀有姓名定义

    在爬取结果的分析方面，“姓名之家”对同一个姓名的查询结果并不稳定，甚至出现迥然不同的结果，例如“皇甫淮琦”的两次查询结果分别为81人和7人。同时，我们测试发现，对于查询结果为“未查询到”的姓名是稳定的。此外，我们对查询结果的统计发现，该网站的查询结果最小值为5人。因此，考虑到结果的准确性，我们定义查询结果为“未查询到”的姓名为稀有姓名。

- 利用官方平台进行数据验证

  抽取了少量样本在全国、上海（小程序）和江苏三个数据源进行了验证，均通过验证

  | 变量名称  | 含义                         | 备注   |
  | --------- | ---------------------------- | ------ |
  | （index） | \                            | 可忽略 |
  | 姓名      | 稀有姓名的具体名称           |        |
  | 总人数    | “姓名之家”网站的相应查询结果 |        |

- ### rarename_list_gen_1124.csv——基于indv数据集构造的姓名集

- 出发点

  由于“姓名之家”重名查询的数据来源并非官方户籍数据，因此怀着对其数据质量的质疑，构造了第二个稀有姓名数据集。根据我们对发明人名字的统计，有近六千个不同的汉字被使用，当两个汉字组合在一起时，大量的名字组合导致名字的分布十分稀疏。因此，拆分成单个汉字可能更能体现姓名的稀有程度。

- 主要过程

  1. 根据indv.txt计算双字名与三字名的比例（四字名极少），再分别计算两者中姓和名的用字分布情况。对于四字姓名则全部保留计算稀有概率
  2. 计算发明人姓名的稀有概率，按比例（约为1：3）选取了40680个稀有姓名。

| 变量名称  | 含义               |
| --------- | ------------------ |
| （index） | \                  |
| inventor  | 稀有姓名的具体名称 |


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

