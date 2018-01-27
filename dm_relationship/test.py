# encoding:utf-8
'''
    功能：根据各类信息，填充domain_conn_dm表，即每个域名第一层关联到的表
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
import database.mysql_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.152','mal_domain_profile')
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')


fetch_data = mongo_conn.mongo_read('domain_conn_dm_test',{'visit_times':1,'links_domains.domains':{'$ne':[]}},{'_id':False,'source_domain':True,'links_domains.domains':True},limit_num = None)
for item in fetch_data:
    source_domain = item['source_domain']
    # print source_domain
    length = len(item['links_domains']['domains'])
    if length > 1000:
        print source_domain
