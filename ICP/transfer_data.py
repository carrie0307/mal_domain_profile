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

sql = "SELECT domain,auth_icp FROM domain_icp WHERE auth_icp != '--';"
fetch_data = mysql_conn.exec_readsql(sql)
counter = 0
for item in fetch_data:
    domain = item[0]
    icp = item[1]
    locate = ICP_pos.get_icp_pos(icp)
    print domain,icp,locate
    sql = "UPDATE domain_icp SET icp_locate = '%s' WHERE domain = '%s';" %(locate,domain)
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
