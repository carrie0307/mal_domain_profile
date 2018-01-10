#-*- coding:utf-8 -*-
import database.mongo_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.152','mal_domain_profile')

fetch_data = mongo_conn.mongo_read('domain_ip_cname',{'domain_ip_cnames.0.ip_state':{'$exists':1}},
                                                    {'domain':True,'domain_ip_cnames':True,'_id':False},limit_num=None
                                    )
for item in fetch_data:
    ip_state_list = item['domain_ip_cnames'][0]['ip_state']
    if ip_state_list:
        # print item['domain']
        for ip_state in ip_state_list:
            if len(ip_state) == 1:
                print item['domain']
                print ip_state
        print '\n'
