#-*- coding:utf-8 -*-
"""
    获取AS信息
    注：
        1. 循环获取时，每次修改last_visit_times的值
        2. 循环获取时先测试一下(尤其注意获取成功和不成功时visittimes的变化)
        3. 注意get_domains()的ip数量
"""

"""数据库模块引入"""
import sys
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.151','mal_domain_profile')

"""IP AS获取引入"""
import ASN.ip_as

"""多线程相关"""
import Queue
import threading
import time

"""线程数量"""
thread_num = 20

"""同步队列"""
domain_q = Queue.Queue()
res_q = Queue.Queue()

"""库中visit_times对应的数值(get_ip_cname已更新visit_times=n,则这里就令visit_times=n)"""
last_visit_times = 5

def get_domains(limit_num = None):
    """
    从数据库中获取要初始获取数据的域名
    注：1 last_visit_times 控制这是对第几次获取的数据获取AS信息
       2 limit_num 控制是否获取一定量的域名
    """
    global mongo_conn
    global last_visit_times
    global domain_q
    global res_q
    global last_visit_times
    cur_array = 'domain_ip_cnames.' + str(last_visit_times - 1) + '.ip_as'

    fetch_data = mongo_conn.mongo_read('domain_ip_cname',{'visit_times':last_visit_times,
                                                        cur_array:{'$exists':False}},
                                                        {'domain':True,'domain_ip_cnames':{'$slice':-1},'_id':False},limit_num
                                        )

    for item in fetch_data:

        ips = item['domain_ip_cnames'][0]['ips'] # 获取上一次新插入的ip
        if ips:
            domain_q.put({item['domain']:ips})
        else:
            # ip序列为空的，as信息也空，直接存储结果
            res_q.put([item['domain'],[]])


def get_asinfo():
    """
        具体为每个域名所对应的ip获取as信息
        param dm_ip_dict: {domain:[ip1,ip2, ..., ipn]}
        return domain,[{ASN:'',ASOWNER:'',...,},{ASN:'',ASOWNER:'',...,},...,{ASN:'',ASOWNER:'',...,}]
    """
    global domain_q
    global res_q

    while not domain_q.empty():
        dm_ip_dict = domain_q.get()
        flag = True # 获取as未出现异常的标志

        domain = dm_ip_dict.keys()[0]
        dm_ip_asinfo = []
        print 'getting ' + domain + ' IP AS info...'

        for ip in dm_ip_dict[domain]:
            try:
                std_asinfo = ASN.ip_as.get_std_asinfo(ip)
                dm_ip_asinfo.append(std_asinfo)
            except Exception, e:
                # 出现异常则停止此域名的相关获取，否则会导致ip和as信息不对应
                domain_q.put(dm_ip_dict) # 将获取失败的域名和ip再次加入队列
                flag = False
                break

        # 未出现异常的as信息获取加入结果队列
        if flag:
            res_q.put([domain,dm_ip_asinfo])
    print 'as信息获取完成...'


def save_asinfo():
    """
    存储as信息
    param: domain :域名
    param: dm_ip_asinfo: [{ASN:'',ASOWNER:'',...,},{ASN:'',ASOWNER:'',...,},...,{ASN:'',ASOWNER:'',...,}]
    """

    global res_q
    global last_visit_times
    cur_array = 'domain_ip_cnames.' + str(last_visit_times - 1) + '.ip_as'

    while True:
        try:
            domain,dm_ip_asinfo = res_q.get(timeout=200)
        except Queue.Empty:
            print '存储完成'
            break

        try:
            mongo_conn.mongo_update('domain_ip_cname',{'domain':domain},{cur_array:dm_ip_asinfo},multi_flag=True)
            print domain + ' saved ...'
        except Exception,e:
            print domain + str(e)
            continue

    print '所有信息存储完成... '



def main():
    """
    集成以上内容的主函数
    """
    print '获取域名...'
    get_domains(limit_num = None)
    get_as_td = []
    for _ in range(thread_num):
        get_as_td.append(threading.Thread(target=get_asinfo))
    for td in get_as_td:
        td.start()
    print 'getting as info ...\n'
    time.sleep(10)
    print 'save as info ...\n'
    save_db_td = threading.Thread(target=save_asinfo)
    save_db_td.start()
    save_db_td.join()


if __name__ == '__main__':
    main()
    '''
    # domain,dm_ip_asinfo = get_asinfo({'0-6-baby.com':["58.222.39.52"]})
    # print domain,dm_ip_asinfo
    # save_asinfo('0-6-baby.com',dm_ip_asinfo)
    '''
