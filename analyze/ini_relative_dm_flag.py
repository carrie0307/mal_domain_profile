# encoding:utf-8
"""
    功能：向吴晓宝学长关联域名库中添加标志位

    author & date: csy 2018.01.17
"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
import database.mysql_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.152','mal_domain_profile')
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')

fetch_data = mongo_conn.mongo_read('links_relation',{'relative_domains':{'$ne':[]}},{'domain':True,'relative_domains':True,'_id':False},limit_num=4)
for item in fetch_data:
    print item['domain'],len(item['relative_domains'])
