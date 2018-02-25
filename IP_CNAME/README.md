# 欢迎使用 Cmd Markdown 编辑阅读器

------

.
├── get_ip_asinfo.py    # 获取as信息总函数（多线程）

├── get_ip_cname.py     # 获取ip,cname信息总函数（单线程）

├── get_ip_cname_td.py  # 获取ip,cname信息总函数（多线程）

├── get_ip_state.py     # 获取ip状态总函数（多线程）

├── __init__.py

├── init_table.py

├── ASN                 # 获取AS信息模块

│   ├── __init__.py

│   ├── ip_as.py        # 获取as信息函数

├── dns_rr              # 获取DNS记录(A,CNAME,NS）模块

│   ├── __init__.py

│   ├── ip_dns_rr.py   # 获取DNS记录函数

├── ip2region          # IP转地理位置模块

│   ├── exec_ip2reg.py  # 封装好的IP转地理位置函数

│   ├── global_region.csv

│   ├── __init__.py

│   ├── ip2region.db   

│   ├── ip2Region.py    # IP转地理位置原始的类

│   ├── ip.merge.txt

│   └── testSearcher.py # 原测试函数

├── nmap_state          # nmap扫描IP端口状态模块

│   ├── __init__.py

│   ├── ip_nmap.py      # nmap扫描端口状态函数

├── README.md


## 运行

* get_ip_cname_td.py
    * 获取每次一轮询的IP、CNAME、NS和IP地理位置信息
    * 假设运行前visit_times = n,则 运行后visit_times=n+1

* get_ip_asinfo.py
    * 获取上一次所得ip的AS信息
    * 假设上次运行get_ip_cname.py后visit_times=n+1，这里就选择visit_times=n+1且没有as信息的数据来获取；更新信息时对应库中domain_ip_cnames列表中的下标是n(visit_times-1)

* get_ip_state.py     
    * 探测上一次所得ip的状态
    * 假设上次运行get_ip_cname.py后visit_times=n+1，这里就选择visit_times=n+1且没有as信息的数据来获取；更新信息时对应库中domain_ip_cnames列表中的下标是n(visit_times-1)
