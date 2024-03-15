1. get_sample.py：数据预处理（挑选A\B\C类专利）
2. get_blocks_json.py：根据需要的features进行block，将计算features需要的变量存入json文件
3. blocks_features_split.py：一个block一个json文件文件太大不好读取，因此选择拆分（引用blocks_features/blocks_split_module.py中的函数）
4. features_scientists_sample.py：阳性样本专利对特征值补充diff_days并合并所有特征值输出features_scientists_pos_new.csv；
5. negative_multiprocess.py：阳性样本中涉及的科学家，其阴性专利对特征值补充diff_days并合并所有特征值输出features_scientists_neg.csv；
6. features_training.py：稀有姓名集按姓名blocks，计算特征值所需的变量拆分成不同txt，存入blocks_split；
7. rarename_blocks_by_surname.py：blocks_split中的稀有姓名按照姓氏重新block，存入rarename_blocks；
8. **get_features_json_threadpool.py**：根据拆分的blocks计算features，存入features_total_split（需要优化）；
9. get_features_json_threadpool_rarename.py：根据拆分的blocks计算稀有姓名集features，存入rarename_features（和get_features_json_threadpool.py结构一致，需要优化）
10. features_sample_xgb_training.py: 稀有姓名集+科学家阳性样本预测模型训练，模型存入model；
11. To be continued...

