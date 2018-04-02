# encoding:utf-8
'''
    功能： 临时代码
'''
import sys
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.151','new_mal_domain_profile')
import datetime

domains = ['00064.com','00066.com','0006sb.com','000888.com','0008sb.com','0011076.com','00052.com']
for domain in domains:
    print domain
    fetch_data = mongo_conn.mongo_read('domain_ip_cname_init',{'domain':domain,},
                                        {'domain':True,'_id':False,'domain_ip_cnames':True},limit_num=1
                                     )
    ip_record = fetch_data[0]['domain_ip_cnames']
    for cur_record in ip_record:
        print cur_record['insert_time']
        if cur_record['ips']:
            for index,ip in enumerate(cur_record['ips']):
                if 'ip_state' in cur_record.keys() and 'AS_cidr' in cur_record.keys():
                    print ip,cur_record['ip_as'][index]['AS_cidr'],'80端口：' + str(cur_record['ip_state'][index]['state80'])
                elif 'AS_cidr' in cur_record.keys():
                    print ip,cur_record['ip_as'][index]['AS_cidr'],'IP状态尚未探测'
                elif 'ip_state' in cur_record.keys():
                    print ip,'AS信息尚未获取','80端口：' + str(cur_record['ip_state'][index]['state80'])
                else:
                    print ip,'AS信息尚未获取','IP状态尚未探测'
        else:
            print '无ip'

    print '\n'
