# features needed

- ### 共同发明人

  ###### 1    record之间共同发明人的数量

- ### 申请人

  ###### 2    共同申请人的个数

  ###### 3    第一申请人的字符串相似度

- ### IPC编码

  ###### 4    共同IPC class的个数

  ###### 5    共同IPC group的个数

- ### 标题

  ###### 6    标题的字符串相似度

  ###### 7    第一个关键词的字符串相似度

  ###### 8    第二个关键词的字符串相似度

- ### 地址——BaiduMap API

  ###### 9    根据七级地址编码，相似等级越高，取值越高。如：相同城市3分，相同镇5分

  ###### 10  地址信息的字符串相似度
  
  | **Feature groups**                   | **Feature** | **Definition**                                   |
  | ------------------------------------ | ----------- | ------------------------------------------------ |
  | **Applicants**                       | app_i       | Number of common members of applicants           |
  |                                      | app_s       | String similarity of first applicants' names     |
  | **Co-inventors**                     | inventor_i  | Number of two records' shared names of inventors |
  | **Technological fields**             | ipc_c       | Number of common members of IPC class            |
  |                                      | ipc_g       | Number of common members of IPC group            |
  | **Technological content of patents** | title       | String similarity of titles                      |
  |                                      | keyword 1   | String similarity of first keywords              |
  |                                      | keyword 2   | String similarity of second keywords             |
  | **Address**                          | address_s   | String similarity of addresses                   |
  |                                      | geo         | 0 from a different country                       |
  |                                      |             | 1 from the same country                          |
  |                                      |             | 2 from the same province                         |
  |                                      |             | 3 from the same city                             |
  |                                      |             | 4 from the same district                         |
  |                                      |             | 5 from the same road or village                  |
  |                                      |             | 6 have the same latitude and longitude           |
  
  



