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

4. 
