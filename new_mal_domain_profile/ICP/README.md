# 非法域名画像 --- icp获取模块

------
## 主要内容

* 从http://icp.chinaz.com获取权威的icp信息，并进行地理位置解析

* 从网站页面获取页面的icp信息与http_code

* 对当前库中page_icp信息进行查重

## 代码功能

.

├── get_chinaz_icp.py  // 单独从站长之家获取icp

├── get_page_icp.py    // 单独从页面获取icp

├── icp_analyze.py     // icp分析

├── icp_general_run.py // 整合后的代码:包括查重分析和icp特征结果分析

├── icp_locate_map.pkl // icp地理位置转化字典文件

├── icp_num.py         // 一个辅助代码

├── ICP_pos.py         // icp地理位置分析(icp_general_run调用)

├── __init__.py

├── ip.py              // ip代理模块

├── log.py             // 日志记录模块(实际未用)

├── myException.py     // 异常模块(ip代理模块调用)

├── page_icp.md        // 页面icp特点分析

├── README.md          // 说明文档

├── test.py            // 临时代码

├── transfer_data.py   // 表之间的数据转移

## 运行

* 先获取基本信息 python icp_general_run.py

* 然后进行分析 python icp_analyze.py

### 获取icp基本信息和地理位置解析结果

* python icp_general_run.py

    * 更新表中auth_icp,icp_locate,page_icp,http_code,get_icp_time子弹，并令flag = flag+1；

    * 当更新时new.auth_icp <> old.auth_icp 或 new.page_icp <> old.page_icp，将通过触发器将原有信息插入到domain_icp_was表中；（即：**当信息发生变化时，原信息会插入domai_icp_was表中；若信息没有变化，则只是更新domain_icp表中时间戳**。）


### icp分析

* python icp_analyze.py
    * page_recheck()  // 查重分析
    * cmp_res()      //结果比对
    * 注意每次运行前更新flag位


## 考虑

* 给icp_general_run添加schedule自动循环运行；

* 在运行icp_general_run.py后，直接用命令调用执行python icp_analyze.py；将flag当作参数传入。
