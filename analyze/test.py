# encoding:utf-8
import sys
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
import database.mysql_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.152','mal_domain_profile')
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')

sql = "SELECT domain,maltype from domain_index;"
fetch_data = mysql_conn.exec_readsql(sql)
for domain,maltype in fetch_data:
    print domain,maltype
    mongo_conn.mongo_update('domain_ip_cname',{'domain':domain},
                                              {'maltype':maltype}
                                              )
