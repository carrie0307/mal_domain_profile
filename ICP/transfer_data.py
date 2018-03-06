# coding=utf-8
import urllib2
import Queue
import threading
import sys
sys.path.append("..") # 回退到上一级目录
import database.mysql_operation
import ICP_pos

'''数据库连接'''
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')

sql = "SELECT domain,auth_icp,page_icp from domain_icp_was where page_icp = '--';"
fetch_data = mysql_conn.exec_readsql(sql)
counter = 0
for item in fetch_data:
    domain = item[0]
    auth_icp = item[1]
    page_icp = item[2]
    print domain,auth_icp,page_icp
    sql = "UPDATE domain_icp_copy SET auth_icp = '%s',page_icp = '%s',get_icp_time = '',flag=1 WHERE domain = '%s';" %(auth_icp,page_icp,domain)
    print sql
    exec_res = mysql_conn.exec_cudsql(sql)
    if exec_res:
        counter += 1
        # print "counter : " + str(counter)
        if counter == 500:
            mysql_conn.commit()
            counter = 0
mysql_conn.commit()
print "存储完成... "
mysql_conn.close_db()
