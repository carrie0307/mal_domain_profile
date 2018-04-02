# 域名及其相关信息关联关系表构建

------

## 表

* domain_general_list 域名总表(对应首页)
* ip_general_list IP总表(对应首页)
* domain_ip_relationship   域名与ip对应关系表
* domain_cname_relationship 域名与cname对应关系表
* reg_info 域名注册信息(包括注册商)表

## 代码


├── build_dm_cname_relationship.py        // 构建域名与cname关系

├── build_domain_ip_relationship.py       // 构建域名与ip关系

├── build_domain_reg_relationship.py      // 构建域名与注册信息关系

├── domain_general_ipinfo.py              // 更新domain_general_list中的ip信息


├── README.md

├── reg_info_count.py                     // 更新reg_info表中信息

└── test.py


## 代码运行顺序

### 第一批

* python reg_info_count.py # 更新reg_info表中信息

* build_domain_ip_relationship.py       # 构建域名与ip关系
    * 功能：
        * 更新ip_general_list中的ip地理位置信息等；

        * 根据domain_ip_relationship更新ip表中的gamble_num,porno_num等；
        * 根据ip_general_list更新domain_ip_relationship的ip地理位置信息

    * 注意
        * mongo中domain_ip_cname每运行一次，这里都要更新；因此要注意visit_times；当mongo中visit_times> mysql中visit_times，就要运行；运行后二者visit_times相等。

    * 根据Mongo中domain_ip_cname更新域名与ip对应关系(每次都取最后一次获取的ip来更新关系(slice=-1))；

    * 注意scan_falg:标识是否扫描记录过这一对应关系(与团体挖掘有关)；

* build_domain_cname_re根据新的ip_general_list中的地理位置信息，更新域名总表中的的ip的地理位置信息lationship.py       # 构建域名与cname关系
    * mongo中domain_ip_cname每运行一次，这里都要更新；因此要注意visit_times；当mongo中visit_times> mysql中visit_times，就要运行；运行后二者visit_times相等每次都取最后一次获取的ip来更新关系(slice=-1)；

    * 注意scan_falg:标识是否扫描记录过这一对应关系；

### 第二批
* python domain_general_ipinfo.py # 更新域名总表中的ip信息

    * 根据domain_ip_relationship更新域名总表domain_general_list中的的ip信息(IP地理位置和IP总数)

    * 根据新的ip_general_list中的地理位置信息，更新域名总表中的的ip的地理位置信息


## 标志位说明

### 主要是针对以下三个表的标志位说明

* domain_ip_relationship   域名与ip对应关系表
* domain_cname_relationship 域名与cname对应关系表
* domain_reg_relationship 域名与注册信息对应关系表
* links_relative

### 标志位

* visit_times(不包括domain_reg_relationship):
 此值与domain_ip_cnames表中的visit_times一致，当domain_ip_cnames表中的visit_times=n,则跑完后就令domain_ip_cnames表中的visit_times为n。

* ip_general_list.whois_detect

标识该IP是否获取过WHOIS信息，默认为0，获取过为1

* scan_flag:  标识该记录是否被domain_conn_dm记录过

    * 每次新导入的关系记为'NEW'

    * 每次conn_domains跑完后，统一通过sql语句将**domain_ip_relationship**，**domain_cname_relationship**，**domain_reg_relationship**表中的scan_flag置为'OLD'。

* relative_domains 和 'domains_enter'的标志位：
    * 在mongo中是与relative_domains.domains和domains_enter.domains一一对应的flag,初值为false,表示此关系尚未被扫描到domain_conn_dm表中；

    * relative_domains.domains和domains_enter.domains每次新添加的域名标志位为false（吴学长）。

    * 每次读取完一个域名的relative_domains关系后，会记录这是哪一个域名，并根据读取出总的relative_domains数量设置flag数列([True] * len(relative_domains.domains))，存入conn_domains中的relative_domains_flag([{'domain':--,flag:[True,...],collection_name:'表名'}])。conn_domains在完成对scan_flag的置数后，根据relative_domains_flag对relative_domains中的flag进行统一置位。
