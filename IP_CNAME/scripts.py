# encoding:utf-8
'''
    功能：同时获取ip，ip的as信息，ip状态
'''
import sys
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.151','new_mal_domain_profile')
import datetime

fetch_data = mongo_conn.mongo_read('domain_ip_cname_history',{'visit_times':1,},
                                                    {'domain':True,'_id':False,'domain_ip_cnames':True},limit_num=10
                                 )
counter = 0
for item in fetch_data:
    num = len(item['domain_ip_cnames'][0]['ips'])
    mongo_conn.mongo_update('domain_ip_cname_history',{'domain':item['domain']},{'domain_ip_cnames.0.num':num,'domain_ip_cnames.0.new':[],'domain_ip_cnames.0.cut':[],'change_times':0})
    counter = counter + 1
    print 'NO.' + str(counter) + ' ' + item['domain']
