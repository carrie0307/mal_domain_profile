# encoding:utf-8
'''
    功能：根据whois表，建立域名注册信息对应关系表
    (目前是每次扫描whois表全部)
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
import database.mysql_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.152','mal_domain_profile')
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')


sql = "SELECT domain,reg_name,reg_email,reg_phone FROM domain_whois;"
fetch_data = mysql_conn.exec_readsql(sql)
for domain,reg_name,reg_email,reg_phone in fetch_data:
    print domain,reg_name,reg_email,reg_phone
    sql = "INSERT domain_reg_relationship(domain,reg_name,reg_email,reg_phone,scan_flag)\
    VALUES('%s','%s','%s','%s','%s')\
    ON DUPLICATE KEY\
    UPDATE scan_flag = '%s';" %(domain,reg_name,reg_email,reg_phone,'NEW','OLD')
    mysql_conn.exec_cudsql(sql)
# sql = "UPDATE domain_ip_relationship SET visit_times = %d;" %(visit_times)
# mysql_conn.exec_cudsql(sql)
mysql_conn.commit()
