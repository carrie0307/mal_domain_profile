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



fetch_data = mongo_conn.mongo_read('domain_conn_dm_test',{'visit_times':1,'links_domains.domains':{'$ne':[]}},{'_id':False,'source_domain':True,'links_domains.domains':True},limit_num = 100)
# fetch_data = mongo_conn.mongo_read('links_relation',{'relative_domains.relative_domains':{'$ne':[]}},{'_id':False,'domain':True,'relative_domains.relative_domains':True},limit_num = 100)
counter = 0
for item in fetch_data:
    # print source_domain
    length = len(item['links_domains']['domains'])

    if length > 100:
        counter += 1
        print 'length: ' + str(length)
        print item['source_domain']
        print counter
