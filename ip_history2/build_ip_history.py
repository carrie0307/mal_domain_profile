# encoding:utf-8
'''
    功能：根据对域名进行轮询解析的结果，填充ip历史信息表
'''
from __future__ import division
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
import database.mysql_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.151','new_mal_domain_profile')
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')
import time

# 1 先取出一个域名的所有ip记录
# 2 检查是否有num位（num表所ip数量，这里也用这一位来标志是否进行过历史记录比对）
# 3 不论是否有变化，都根据ip数量置num的值
# 4 将这一次的数据与前一次的比对，若有变化，则change+=1,并记录new,cut;
# 5 cidr问题：
# for ip in new:
#     addtoset {ip:---,'cidr':---} # 如果此次新增的ip以前已经记录过其对应的ip-cidr，则addtoset会自动去重
# 6 频率计算：
#  每次读出域名ip的全部记录时，不论是否变化，都检查new cut有没有不为空的，如果有，则说明发生了变化， 令计数器+1



def diff_list(list1,list2):
    '''
    功能：求两个列表差集(list1有但list2没有的元素)
    '''
    retD = list(set(list1).difference(set(list2)))
    return retD


def get_single_domain_record(domain):
    '''
    功能：取出一个域名的所有ip记录（对应步骤1）
    '''
    fetch_data = mongo_conn.mongo_read('domain_ip_cname',{'domain':domain},
                                            {
                                            'domain':True,
                                            '_id':False,
                                            'domain_ip_cnames':True
                                            },
                                        limit_num = None
                                       )
    if fetch_data:
        domain = fetch_data[0]['domain']
        domain_ip_cnames = fetch_data[0]['domain_ip_cnames']

    return domain,domain_ip_cnames


def cmp_whether_change(domain_ip_cnames):
    '''
    功能：对n次的ip/cname记录进行比对处理 （对应步骤2,3,4）
    '''
    cidr_list = []
    counter = 0 # ip发生变化计数器
    for index,record in enumerate(domain_ip_cnames):
        if 'num' not in record.keys():# 说明没有进行过比对(步骤2)
                # 先置ip数量 （步骤3）
                domain_ip_cnames[index]['num'] = len(domain_ip_cnames[index]['ips'])

                if index == 0:
                    domain_ip_cnames[index]['cut'] = []
                    domain_ip_cnames[index]['new'] = []
                    # for i,ip in enumerate(domain_ip_cnames[index]['ips']):
                        # print '---'
                        # as_cidr = domain_ip_cnames[index]['ip_as'][i]['AS_cidr']
                        # print as_cidr
                else:
                    cur_ips = record['ips'] # 当前ip
                    last_time_ips = domain_ip_cnames[index - 1]['ips'] # 上一次的ip记录

                    domain_ip_cnames[index]['new'] = diff_list(cur_ips,last_time_ips) # 求新增ip
                    domain_ip_cnames[index]['cut'] = diff_list(last_time_ips,cur_ips) # 求减少ip

                    # if domain_ip_cnames[index]['new']: # 如果较之上次有了新增的ip，则看是否增加了新的ip-ascidr对
                        # for i,ip in enumerate(domain_ip_cnames[index]['ips']):
                            # as_cidr = domain_ip_cnames[index]['ip_as'][i]['AS_cidr']
                            # print as_cidr

        if domain_ip_cnames[index]['new'] or domain_ip_cnames[index]['cut']: #步骤6
            # 如果有新增或减少的ip
            counter += 1
    print counter
    print index+1
    frequency = round(counter / (index+1),2) # (index+1是len(domain_ip_cnames))
    frequency = str(counter) + '/' + str(index+1) + '(' + str(frequency) + ')'
    print frequency


if __name__ == '__main__':
    domain,domain_ip_cnames = get_single_domain_record('0-360c.com')
    # for record in domain_ip_cnames:
    #     print record['ips']
    # print '\n'
    cmp_whether_change(domain_ip_cnames)
    # for record in domain_ip_cnames:
    #     print record['ips']
    #     print 'new:', record['new']
    #     print 'cut:', record['cut']
    #     print 'num:', record['num']
    #     print '\n'
