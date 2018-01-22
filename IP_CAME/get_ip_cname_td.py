# encoding:utf-8

"""
    使用阿里114DNS获取域名NS记录，A记录和CNAME记录
    注：1.每次运行注意更新last_visit_times的数
       2. 循环获取前先测试一下(尤其注意获取成功和不成功时visittimes的变化)
       3. 注意get_domains()的ip数量
"""

import dns_rr.ip_dns_rr
import tldextract
from datetime import datetime

import sys
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.152','mal_domain_profile')
"""与库中visit_times相对应"""
last_visit_times = 2

"""多线程相关"""
import Queue
import threading
import time

"""线程数量"""
thread_num = 20

"""同步队列"""
domain_q = Queue.Queue()
res_q = Queue.Queue()

"""地理位置相关"""
import ip2region.ip2Region
import ip2region.exec_ip2reg
searcher = ip2region.ip2Region.Ip2Region("ip2region/ip2region.db")

"""获取记录超时时间"""
timeout = 20

"""阿里114DNS"""
server = '1.2.4.8'


def get_domains(limit_num = None):
    """
    从数据库中获取要初始获取数据的域名
    注：1 last_visit_times 控制这是第几次获取
       2 limit_num 控制是否获取一定量的域名
    """
    global domani_q
    global mongo_conn
    global last_visit_times
    domain_list = []

    fetch_data = mongo_conn.mongo_read('domain_ip_cname',{'visit_times':last_visit_times},{'domain':True},limit_num)
    domains = list(fetch_data)
    for domain in domains:
        domain_q.put(domain['domain'])
    # return domain_list


def insert_data():
    global mongo_conn
    global res_q
    collection_name = 'domain_ip_cname'

    while True:
        try:
            check_domain, cnames, ips, ns, ips_geo_list = res_q.get(timeout=200)
        except Queue.Empty:
            print '存储完成...'

        # 组装信息
        detect_res = {}
        detect_res['cnames'] = cnames
        detect_res['NS'] = ns
        detect_res['ips'] = ips
        detect_res['ip_geo'] = ips_geo_list
        detect_res['insert_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        cur_array = 'domain_ip_cnames.' + str(last_visit_times) # 当前domain_ip_cnames下标

        try:
            # 更新visit_time的值
            mongo_conn.mongo_inc(collection_name,{'domain':check_domain},{'visit_times':1})
            # 添加ip_cname的值
            domain_ip_cnames = mongo_conn.mongo_update(collection_name,{'domain':check_domain},
                                                        {cur_array:detect_res}
                                                      )
            print check_domain + '  saved ...'
        except Exception,e:
            print check_domain + ' save ' + str(e)
            # pass

    print '所有数据存储完成...'


def get_ip_ns_cname_handler():
    global searcher
    global domain_q
    global res_q

    while not domain_q.empty():

        check_domain = domain_q.get()
        g_ns, g_ips, g_cnames, ips_geo_list = [], [], [], []

        ## 提取domain+tld
        domain_tld = tldextract.extract(check_domain)
        if domain_tld.suffix == "":
            return []
        else:
            check_domain = domain_tld.domain+'.'+domain_tld.suffix

        fqdn_domain = 'www.' + check_domain  # 全域名
        print '查询的域名：',check_domain   # 在查询的域名

        try:
            """取消了被封装函数中的异常处理，所有异常在这里统一捕获处理"""
            dns_rr.ip_dns_rr.fetch_rc_ttl(fqdn_domain,g_ns, g_ips, g_cnames)
        except Exception,e:
            """凡是捕获到异常的，均加入队列统一再获取一遍(因为有些总是出现异常，因此直接存空结果)"""
            # domain_q.put(check_domain)
            print check_domain,str(e)

        for ip in g_ips:
            # 获取ip地理为值信息
            ip_geo_info = ip2region.exec_ip2reg.get_ip_geoinfo(searcher,ip)
            ips_geo_list.append(ip_geo_info)

        # 向结果队列中添加内容
        res_q.put([check_domain, g_cnames, g_ips, g_ns, ips_geo_list])



def main():
    get_domains(limit_num = None)
    get_dns_td = []
    for _ in range(thread_num):
        get_dns_td.append(threading.Thread(target=get_ip_ns_cname_handler))
    for td in get_dns_td:
        td.start()
    print 'getting dns info ...\n'
    time.sleep(5)
    print 'save dns info ...\n'
    save_db_td = threading.Thread(target=insert_data)
    save_db_td.start()
    save_db_td.join()



if __name__ == '__main__':
    main()
    # g_ns, g_ips, g_cnames, ips_geo_list = [], [], [], []
    # dns_rr.ip_dns_rr.fetch_rc_ttl('www.0-360c.com',g_ns, g_ips, g_cnames)
    # print g_ns, g_ips, g_cnames
