# encoding:utf-8
'''
    功能：同时获取ip，ip的as信息，ip状态
'''
import sys
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.151','new_mal_domain_profile')
import datetime
import schedule

"""多线程相关"""
import Queue
import threading
import time

"""插入时间"""
import datetime

"""ip，ns获取相关"""
import dns_rr.ip_dns_rr
import tldextract


"""地理位置相关"""
import ip2region.ip2Region
import ip2region.exec_ip2reg
searcher = ip2region.ip2Region.Ip2Region("ip2region/ip2region.db")

"""IP AS获取引入"""
import ASN.ip_as

"""IP state获取引入"""
import nmap_state.ip_nmap

"""获取前的visit_times是多少"""
last_visit_times= 4

domain_q = Queue.Queue()
res_q = Queue.Queue()
thread_num = 1


def get_ip_ns_cname(check_domain):
    '''
    功能：DNS解析获取ip记录/获取ip地理位置信息
    '''

    global searcher

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

    return g_cnames,g_ips,g_ns,ips_geo_list



def get_asinfo(ips):
    """
        功能：具体为每个域名所对应的ip获取as信息
        :param ips:ip列表[ip1,ip2,.....](某个域名的ip列表)
        return domain,[{ASN:'',ASOWNER:'',...,},{ASN:'',ASOWNER:'',...,},...,{ASN:'',ASOWNER:'',...,}]
    """
    # ips为空列表时，直接返回[]
    if not ips:
        return []

    flag = True # 获取是否出现异常标志位
    as_info = []
    for ip in ips:
        try:
            std_asinfo = ASN.ip_as.get_std_asinfo(ip)
            as_info.append(std_asinfo)
        except Exception, e:
            # 出现异常则停止此域名的相关获取，否则会导致ip和as信息不对应
            flag = False
            break
    # 未出现异常的as信息获取加入结果队列
    if flag:
        # print as_info
        print 'as信息获取完成...'
        return as_info
    else:
        print '出现异常重新获取as信息...'
        return get_asinfo(ips)



def get_ip_state(ips):
    """
    功能：调用/nmap_state/ip_nmap中通过nmap扫描ip端口的函数
    :param ips:ip列表[ip1,ip2,.....](某个域名的ip列表)
    """
    # ips为空列表时，直接返回[]
    if not ips:
        return []

    flag = True # 获取是否出现异常标志位
    ip_state_list = []
    for ip in ips:
        try:
            print 'getting ' + ip + '  state ...'
            ip_state = nmap_state.ip_nmap.get_nmap_state(ip)
            ip_state_list.append(ip_state)
        except Exception, e:
            # 出现异常则停止此域名的相关获取，否则会导致ip和as信息不对应
            print ip,str(e)
            flag = False
            break
    # 未出现异常的status信息获取加入结果队列
    if flag:
        # print ip_state_list
        print 'ip状态信息获取完成...'
        return ip_state_list
    else:
        print '出现异常重新获取ip状态...'
        return get_ip_state(ips)


def get_domains(limit_num = None):
    """
    从数据库中获取要初始获取数据的域名
    注：1 last_visit_times 控制这是对第几次获取的数据获取AS信息
       2 limit_num 控制是否获取一定量的域名
    """
    global mongo_conn
    global last_visit_times
    global domain_q

    # 本次ip状态信息对应的下标，用于判断是否已存在此次信息
    # cur_array = 'domain_ip_cnames.' + str(last_visit_times - 1) + '.ip_state'

    # 根据visit_times获取控制获取的域名，然后直接获取域名传递给获取数据的函数
    fetch_data = mongo_conn.mongo_read('domain_ip_cname',{'visit_times':last_visit_times,},
                                                        {'domain':True,'_id':False},limit_num
                                     )
    for item in fetch_data:
        domain_q.put(item['domain'])

def save_data():
    '''
    功能：存储ip相关信息
    '''
    global mongo_conn
    global res_q

    # cur_array = 'domain_ip_cnames.' + str(last_visit_times)

    while True:
        try:
            domain,res = res_q.get(timeout=30)
        except Queue.Empty:
            print '存储完成'
            break

        try:
            mongo_conn.mongo_any_update('domain_ip_cname',{'domain':domain},
                                        {
                                            '$inc':{'visit_times':1},
                                            '$push':{'domain_ip_cnames':{'$each':res}}
                                        })
            print domain + ' saved ...'
        except Exception,e:
            print domain + str(e)
            continue


def run():
    '''
    功能：调用以上三个函数，一次性完次ip相关信息的获取
    '''
    global domain_q
    global res_q

    while not domain_q.empty():
        check_domain = domain_q.get()

        cnames,ips,ns,ips_geo_list = get_ip_ns_cname(check_domain)
        ip_as = get_asinfo(ips)
        ip_state_list = get_ip_state(ips)

        insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        res = {'ips':ips,'NS':ns,'ip_geo':ips_geo_list,'cnames':cnames,'ip_as':ip_as,'ip_state':ip_state_list,'insert_time':insert_time}
        res = [res]
        res_q.put([check_domain,res])
        print check_domain
        print res

    print '获取完成...'


def main():
    # 获取域名
    global last_visit_times
    last_visit_times += 1
    print 'start:  ', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    get_domains(limit_num = None)
    get_state_td = []
    for _ in range(thread_num):
        get_state_td.append(threading.Thread(target=run))
    for td in get_state_td:
        td.start()
    time.sleep(5)
    print 'save ip general info ...\n'
    save_db_td = threading.Thread(target=save_data)
    save_db_td.start()
    save_db_td.join()
    print 'end:   ', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))


schedule.every(2).minutes.do(main())

if __name__ == '__main__':

    while True:
        schedule.run_pending()
        time.sleep(1)

    # schedule.every().hour.do(job)

    # main()
    # g_cnames,g_ips,g_ns,ips_geo_list = get_ip_ns_cname('baidu.com')
    # get_asinfo(g_ips)
    # get_ip_state(g_ips)
