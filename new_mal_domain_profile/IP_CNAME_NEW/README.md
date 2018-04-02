# 欢迎使用 Cmd Markdown 编辑阅读器

------
.

├── dns_rr                 // DNS记录探测目录
│   ├── __init__.py

│   ├── ip_dns_rr.py     // DNS记录探测

│   ├── ip_dns_rr_small.py   // 小部分数据DNS记录探测(NS,A)

├── dns_rr_detect_loop.py    // 循环进行DNS探测

├── encode_deal.py           // 存储结果的编码处理

├── get_respectively         // 单独进行ip,AS信息，CNAME,获取的代码
│   ├── get_ip_asinfo.py

│   ├── get_ip_cname_loop.py

│   ├── get_ip_cname.py

│   ├── get_ip_cname_td.py

│   └── get_ip_state.py

├── __init__.py

├── ip2region                // IP地理位置转化代码

│   ├── exec_ip2reg.py

│   ├── global_region.csv   

│   ├── __init__.py

│   ├── ip2region.db

│   ├── ip2Region.py

│   ├── ip.merge.txt

│   └── testSearcher.py

├── README.md

├── scripts.py

└── small_dns_rr_detect_loop.py    // 小部分数据循环探测代码


## 运行

* python dns_rr_detect_loop.py
    从域名主表获取域名进行探测
