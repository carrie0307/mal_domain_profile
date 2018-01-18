# encoding:utf-8
"""
    功能：初始化导入空数据和表结构
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
import database.mysql_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.152','mal_domain_profile')
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')


sql = "SELECT domain FROM domain_index;"
fetch_data = mysql_conn.exec_readsql(sql)
documents = []
for item in fetch_data:
    domain = item[0]
    single_document = {'source_domain':domain,
    'ip_domains':{'domains':{},'reg_info':{}},
    'cname_domains':{'domains':{},'reg_info':{}},
    'reg_email_domainn':{'conn':'','domains':[],'reg_info':[]},
    'reg_phone_domainn':{'conn':'','domains':[],'reg_info':[]},
    'reg_name_domainn':{'conn':'','domains':[],'reg_info':[]},
    'links_domains':{'domains':[],'reg_info':{}},
    }
    documents.append(single_document)


mongo_conn.mongo_insert('domain_conn_dm',documents)
