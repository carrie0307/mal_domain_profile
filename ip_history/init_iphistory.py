# encoding:utf-8
'''
    功能：根据对域名进行轮询解析的结果，填充ip历史信息表
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
import database.mysql_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.152','mal_domain_profile')
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')



fetch_data = mongo_conn.mongo_read('domain_ip_cname',{},{'domain':True,'_id':False,'domain_ip_cnames':{'$slice':1}},limit_num = None)
documents = []
for item in fetch_data:

    temp = dict(domain=item['domain'],
                ip_history = [],
                ip_cidr_list = []
                )
    documents.append(temp)

mongo_conn.mongo_insert('ip_history',documents)




#
# insert_time = item['domain_ip_cnames'][0]['insert_time'],
# ip_num = len(item['domain_ip_cnames'][0]['ips']),
# ips = item['domain_ip_cnames'][0]['ips'],
# ip_state = item['domain_ip_cnames'][0]['ip_state']
# ip_as = item['domain_ip_cnames'][0]['ip_as']
