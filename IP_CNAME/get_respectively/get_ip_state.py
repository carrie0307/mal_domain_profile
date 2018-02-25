#-*- coding:utf-8 -*-
"""
    nmap扫描获取主机与80,443端口状态
    注：
        1. 循环获取时，每次修改last_visit_times的值
        2. 循环获取时先测试一下(尤其注意获取成功和不成功时visittimes的变化)
        3. 注意get_domains()的ip数量
"""

"""数据库模块引入"""
import sys
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.152','mal_domain_profile')

"""IP state获取引入"""
import nmap_state.ip_nmap

"""多线程相关"""
import Queue
import threading
import time

"""线程数量"""
thread_num = 5

"""同步队列"""
domain_q = Queue.Queue()
res_q = Queue.Queue()

"""库中visit_times对应的数值(get_ip_cname已更新visit_times=n,则这里就令visit_times=n)"""
last_visit_times = 3


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

    # 本次ip状态信息对应的下标，用于判断是否已存在此次信息
    cur_array = 'domain_ip_cnames.' + str(last_visit_times - 1) + '.ip_state'

    # slice = -1 每次只获取最后一次的ip信息
    fetch_data = mongo_conn.mongo_read('domain_ip_cname',{'visit_times':last_visit_times,
                                                        cur_array:{'$exists':False}},
                                                        {'domain':True,'domain_ip_cnames':{'$slice':-1},'_id':False},limit_num
                                        )
    for item in fetch_data:

        print item['domain']
        ips = item['domain_ip_cnames'][0]['ips'] # 获取上一次新插入的ip
        if ips:
            domain_q.put({item['domain']:ips})
        else:
            # ip序列为空的，as信息也空，直接存储结果
            res_q.put([item['domain'],[]])


def get_ip_state():
    """
    调用/nmap_state/ip_nmap中通过nmap扫描ip端口的函数
    """
    global domain_q
    global res_q

    while not domain_q.empty():
        dm_ip_dict = domain_q.get()
        flag = True # 获取status未出现异常的标志

        domain = dm_ip_dict.keys()[0]
        dm_ip_state = []
        print 'getting ' + domain + ' IP state ...'

        for ip in dm_ip_dict[domain]:
            try:
                print 'getting ' + ip + 'state ...'
                ip_state = nmap_state.ip_nmap.get_nmap_state(ip)
                dm_ip_state.append(ip_state)
            except Exception, e:
                # 出现异常则停止此域名的相关获取，否则会导致ip和as信息不对应
                print ip,str(e)
                flag = False
                break

        # 未出现异常的status信息获取加入结果队列
        if flag:
            res_q.put([domain,dm_ip_state])
    print 'ip状态信息获取完成...'




def save_state_info():
    """
    存储ip status信息
    param: domain :域名
    param: ip_state: [{'state80':, 'state': 'state443': },{'state80':, 'state': 'state443': },...,{'state80':, 'state': 'state443': }]

    三种情况：
    1. 当ip列表为空时，ip_state=[](在get_domains中返回了)
    2. 对ip的扫描结果没有scan字段 [{'state80':0, 'state':0 'state443':0 },{'state80':, 'state': 'state443': },...,{'state80':, 'state': 'state443': }]
    3. 返回正常扫描结果
    """

    global res_q
    global last_visit_times
    cur_array = 'domain_ip_cnames.' + str(last_visit_times - 1) + '.ip_state'

    while True:
        try:
            domain,dm_ip_asinfo = res_q.get(timeout=600)
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
    get_domains(limit_num = 10)
    get_state_td = []
    for _ in range(thread_num):
        get_state_td.append(threading.Thread(target=get_ip_state))
    for td in get_state_td:
        td.start()
    print 'getting ip state ...\n'
    # time.sleep(10)
    print 'save state info ...\n'
    save_db_td = threading.Thread(target=save_state_info)
    save_db_td.start()
    save_db_td.join()


if __name__ == '__main__':
    main()
    # ip = '112.121.172.146'
    # print get_nmap_state(ip)
