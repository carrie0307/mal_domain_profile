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
import time

# 标志现在取回的是第几次的数据
visit_times = 2

# slice获取数据的分割
start = 0
skip = 2


def diff_list(list1,list2):
    '''
    功能：求两个列表差集(list1有但list2没有的元素)
    '''
    retD = list(set(list1).difference(set(list2)))
    return retD


def save_new_info(domain,ip_record,ip_cidr_list):
    '''
    功能：向ip_history表中添加新一次的ip信息（增减情况）及cidr情况
    param: domain :域名
    param: ip_record: 一次域名的相关信息
    param: ip_cidr_list: 更新ip_cidr相关信息
        ip_record:
           {
                 #一次的ip探测结果
                insert_time:--, # 该次ip探测时间
                num:--,         # 该次ip数量
                ips:[],         # 该次ip序列
                ip_state:[],    # 对应的ip_states
                new:[],         # 较上次新增ip
                cut:[],         # 较上次减少ip
            }
        ip_cidr_list:
        '''
    operation = {'$push':{'ip_history':ip_record},'$addToSet':{'ip_cidr_list':{'$each':ip_cidr_list}}}
    mongo_conn.mongo_any_update('ip_history_test',{'domain':domain},operation)


def deal_with_ipinfo(item):
    '''
    功能：对某个域名的ip相关信息进行处理
    param: item = {domain:---,domain_ip_cnames:[]} 与domain_ip_cname表对应
    return: ip_record: 该次ip处理后的结果
    return: ip_cidr_list: 根据此结果得到的cidr-ip的pairs
    '''
    global visit_times

    ip_cidr_list,new,cut = [],[],[] # ip-cidr对应的数列，新增ip数列和减少ip数列

    if visit_times != 1: # 获取的不是第一次的数据，则需要进行两次的比对，得到new和cut
        # 新增ip
        new = diff_list(item['domain_ip_cnames'][1]['ips'],item['domain_ip_cnames'][0]['ips'])
        # 减少ip
        cut = diff_list(item['domain_ip_cnames'][0]['ips'],item['domain_ip_cnames'][1]['ips'])

    ips = item['domain_ip_cnames'][-1]['ips']
    as_info = item['domain_ip_cnames'][-1]['ip_as']

    for ip,ip_as in zip(ips,as_info):
        # print ip,ip_as['AS_cidr']
        cidr = ip_as['AS_cidr']
        ip_cidr_list.append({'ip':ip,'cidr':cidr})

    ip_record = dict(
                insert_time=item['domain_ip_cnames'][-1]['insert_time'],
                ip_num = len(ips),
                ips = ips,
                ip_state = item['domain_ip_cnames'][-1]['ip_state'],
                new = new,
                cut = cut
                )

    return ip_record,ip_cidr_list



def main():
    global visit_times
    global start,skip

    fetch_data = mongo_conn.mongo_read('domain_ip_cname',{},
                                           {'domain':True,'_id':False,
                                           'domain_ip_cnames':{'$slice':[start,skip]}},limit_num = None
                                       )
    start = time.time()

    for item in fetch_data:
        domain = item['domain']
        print domain
        ip_record,ip_cidr_list = deal_with_ipinfo(item)
        save_new_info(domain,ip_record,ip_cidr_list)
        print str(time.time() - start) + '\n'

if __name__ == '__main__':
    main()
