# 非法域名画像 --- IP/CNAME及相关信息获取模块

------

## 代码

* domain_ip_cname.py   
    * 获取IP、CNAME和NS记录的原始数值

* ip2regio/exec_ip2reg.py
    * 获取IP的地理位置与运营商

* ip_asn.py
    * 获取IP的AS信息
    * AS_insert_time:获取as信息的时间

* ip_nmap.py
    * 通过nmap获取主机与80，443端口的状态
    * status_insert_time:扫描状态的时间

## 运行

* domain_ip_cname.py   
    * 获取IP、CNAME和NS记录的原始数值
    * 把ip2regio/exec_ip2reg.py所得的地理位置信息也封装进去
    * 总的insert_time

* ip_asn.py
    * 获取ASN信息
    * 注意存AS信息时的操作
    * AS_insert_time:获取as信息的时间

* ip_nmap.py
    * 通过nmap获取主机与80，443端口的状态
    * 注意存库
    * status_insert_time:扫描状态的时间

* 循环获取IP
    * 每次向domain_ip_cname中添加domain_ip_cname.py运行结果
    * 更新visit_times数值

# 问题
    * 递归服务器选择
    * domain_ip_cname能否添加多线程
    * AS信息和nmap状态添加多线程


---
2018.01.06
