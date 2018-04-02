#-*- coding:utf-8 -*-
import database.mongo_operation
mongo_conn = database.mongo_operation.MongoConn('10.245.146.38','new_mal_domain_profile')


res = [{'ips':['1.2.3.4']}]
fetch_data =mongo_conn.mongo_read('domain_ip_cname_test',{'domain':'baidu.com'},{'domain':True},limit_num = 1)
print list(fetch_data)
mongo_conn.mongo_any_update_new('domain_ip_cname_test',{'domain':'1688.com'},
                                                    {
                                                    '$set':{'domain':'1688.com','illegal_type':'gamble'},
                                                    '$inc':{'visit_times':1},
                                                    '$push':{'domain_ip_cnames':{'$each':res}}
                                                    },
                                                    True
                            )
print '---'
