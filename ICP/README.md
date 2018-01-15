# 非法域名画像 --- icp获取模块

------
## 主要内容

* 从[站长之家](http://icp.chinaz.com)获取icp信息：

    * python get_chinaz_icp.py（注意修改表名）

    * 这里存在被ban的情况，采用了之前写的ip_proxy工具。但是由于获取ip代理时也可能被ban，因此会有一些报错信息产生，但并未影响程序的正常获取

* 从网站页面上获取icp信息：

    * python get_page_icp.py（注意修改表名）

* 站长之家icp与页面icp的一致性比对

    * python cmp.py （注意修改表名）

    * 具体比对方式见代码中注释

* icp信息的查重

    * python duplicate_icp.py （注意修改表名）

    * 具体查重方式见代码中注释

## 运行与存储相关说明:

* 运行顺序(从逻辑和flag位2方面确定)

    * auth_icp 获取
    * page_icp 获取
    * icp查重
    * icp比对

* 数据库flag位

以2进制为对应
|icp_duplicate| icp_cmp | page_icp | auth_icp |
| ------------- |:-------------:| :-----:|-----:|
| 8      | 4 | 2 |1 |


* 获取auth_icp前:
    flag = 0
* 获取auth_icp后:
    flag = flag + 1,即 flag = 1

* 获取page_icp前:
    flag = 0 或 flag = 1, 即 flag < 2
* 获取auth_icp后:
    flag = flag + 2， 即 flag = 3

* icp_cmp前
    flag = 3
* icp_cmp后:
    flag + 4

* icp查重(针对page_icp)前
    3 <= flag < 8
* 查重后:
    flag + 8
    flag >= 8
