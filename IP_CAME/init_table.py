# coding=utf-8
'''
    初始化运行IP/CNAME的表
'''
import sys
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
import database.mysql_operation

"""mongo连接"""
mongo_conn = database.mongo_operation.MongoConn('172.29.152.152','mal_domain_profile')

"""mysql连接"""
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')

domains = []
sql = "SELECT domain FROM domain_index;"
fetch_data = mysql_conn.exec_readsql(sql)
for domain in fetch_data:
    domains.append(domain[0])
mysql_conn.close_db()

domain_documents = []
for domain in fetch_data:
    domain_documents.append({'domain':domain[0],'domain_ip_names':[],'visit_times':0})

mongo_conn.mongo_insert('domain_ip_cname',domain_documents)
