# encoding:utf-8
'''
    功能：一小部分数据循环探测IP与IP端口状态
'''
import nmap
import sys
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
import database.mysql_operation
reload(sys)
sys.setdefaultencoding('utf-8')
mongo_conn = database.mongo_operation.MongoConn('10.245.146.38','illegal_domains_profile')
import datetime
import schedule

"""多线程相关"""
import Queue
import threading
import time

"""插入时间"""
import datetime

"""ip，ns获取相关"""
import dns_rr.ip_dns_rr_small
import tldextract

"""编码处理"""
import encode_deal


"""地理位置相关"""
import ip2region.ip2Region
import ip2region.exec_ip2reg
searcher = ip2region.ip2Region.Ip2Region("ip2region/ip2region.db")

domain_q = Queue.Queue()
res_q = Queue.Queue()
thread_num = 2
collection_name = 'domain_dns_rr_small'


def get_ip_rr_cname(check_domain):
    '''
    功能：DNS解析获取资源记录/获取ip地理位置信息
    '''

    global searcher

    g_ns, g_ips, g_cnames, ips_geo_list = [], [], [], []
    dns_message = []

    ## 提取domain+tld
    print check_domain
    domain_tld = tldextract.extract(check_domain)
    if domain_tld.suffix == "":
        return []
    else:
        check_domain = domain_tld.domain+'.'+domain_tld.suffix

    fqdn_domain = 'www.' + check_domain  # 全域名
    print '查询的域名：',check_domain   # 在查询的域名

    try:
        # """取消了被封装函数中的异常处理，所有异常在这里统一捕获处理"""
        dns_rr.ip_dns_rr_small.get_complete_dns_rr(fqdn_domain, g_ns, g_ips, g_cnames, dns_message)
    except Exception,e:
        """凡是捕获到异常的，均加入队列统一再获取一遍(因为有些总是出现异常(No address associated with hostname)，因此直接存空结果)"""
        if str(e) == '[Errno -3] Temporary failure in name resolution':
            # 应该时连接过多的导致，因此sleep一段时间,再重新获取
            print '暂停等待连接关闭...'
            time.sleep(300)
            print '重新开始获取...'
            domain_q.put(check_domain)
        elif str(e) == 'Timeout':
            # 超时错误则加入队列再进行获取
            domain_q.put(check_domain)
        elif str(e) == '[Errno -2] Name or service not known':
            # 应该是ns无法解析该域名的情况;这种情况下ns记录可能时已经获取到的，例如 000082.com
            dns_message = 'Name or service not known'
        print check_domain,str(e)

    for ip in g_ips:
        # 获取ip地理为值信息
        ip_geo_info = ip2region.exec_ip2reg.get_ip_geoinfo(searcher,ip)
        ips_geo_list.append(ip_geo_info)
    # print g_cnames,g_ips,g_ns,ips_geo_list,g_soa, g_txt, g_mx,dns_message
    return g_cnames,g_ips,g_ns,ips_geo_list,dns_message


def get_domains():
    """
    从数据库中获取要初始获取数据的域名
    注：1 limit_num 控制是否获取一定量的域名
    """
    global domain_q

    fetch_data = mongo_conn.mongo_read(collection_name,{'visit_times':0}, {'domain':True,'_id':False,'visit_times':True},limit_num=None)
    for item in fetch_data:
        domain_q.put(item['domain'])


def save_data():
    '''
    功能：存储ip相关信息
    '''
    global mongo_conn
    global res_q
    global collection_name

    while True:
        try:
            domain,res,changed = res_q.get(timeout=3600)
        except Queue.Empty:
            print '存储完成'
            break

        try:
            mongo_conn.mongo_any_update_new(collection_name,{'domain':domain},
                                                                {
                                                                '$inc':{'visit_times':1,'change_times':changed},
                                                                '$push':{'domain_ip_cnames':res}
                                                                # '$push':{'domain_ip_cnames':{'$each':res}}
                                                                },
                                                                True
                                        )

            print domain + ' saved ...'
        except Exception,e:
            print domain + str(e)
            continue


def diff_list(list1,list2):
    '''
    功能：求两个列表差集(list1有但list2没有的元素)
    '''
    retD = list(set(list1).difference(set(list2)))
    return retD


def cmp_whether_chagne(check_domain,res):
    '''
    前后两次ip比对是否发生了变化
    '''
    global collection_name
    changed = 1 # 标志是否发生了变化

    fetch_data = mongo_conn.mongo_read(collection_name,{'domain':check_domain,},
                                                                 {'domain':True,
                                                                  'domain_ip_cnames':{'$slice':-1},
                                                                  '_id':False
                                                                 },limit_num=1
                                      )
    if fetch_data and fetch_data[0]['domain_ip_cnames']:
        # 上一次的ip集合
        last_time_ips = fetch_data[0]['domain_ip_cnames'][0]['ips']
        # 这一次的ip集合
        ips = res['ips']
        new = diff_list(ips,last_time_ips)
        cut = diff_list(last_time_ips,ips)
        # 如果哦new和cut都是[],则说明没有发生变化
        if not new and not cut:
            changed = 0
    else:
        # 说明是第一次入库的域名
        changed = 0
        new,cut = [],[]

    res['new'] = new
    res['cut'] = cut
    return changed


def nmap_get_ip_state(ips):
    '''
    通过NMAP获取IP状态
    '''
    ip_state_list = []

    try:
        nm = nmap.PortScanner()
    except nmap.PortScannerError:
        return ip_state_list

    for ip in ips:
        ip_info = {'state':'--', 'state80':'--', 'state443':'--','exception_message':'--'}

        try:
            res = nm.scan(ip,'80,443')
        except Exception,e:
            ip_info['exception_message'] = 'Scan Error: ' + str(e)
            return ip_info

        if res['scan'] and 'status' in res['scan'][ip]:
            # 获取主机状态信息
            ip_info['state'] = res['scan'][ip]['status']['state']

        if res['scan'] and 'tcp' in res['scan'][ip]:
            # 获取各个端口信息
            for port in res['scan'][ip]['tcp']:
                if port == 80:
                    ip_info['state80'] = res['scan'][ip]['tcp'][port]['state']
                elif port == 443:
                    ip_info['state443'] = res['scan'][ip]['tcp'][port]['state']
        ip_state_list.append(ip_info)

    return ip_state_list

def run():
    '''
    功能：调用以上三个函数，一次性完次ip相关信息的获取
    '''
    global domain_q
    global res_q

    while not domain_q.empty():
        check_domain = domain_q.get()
        cnames,ips,ns,ips_geo_list,dns_message = get_ip_rr_cname(check_domain)
        ip_state_list = nmap_get_ip_state(ips)
        insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        res = {
             'ips':ips,'NS':ns,'ip_geo':ips_geo_list,
             'cnames':cnames,'new':[],'cut':[],'ip_state':ip_state_list,
             'insert_time':insert_time,'dns_message': dns_message
             }

        # 编码处理
        encode_deal.dict_encode_deal(res)
        # 是否发生改变标志
        changed = cmp_whether_chagne(check_domain,res)
        res['changed'] = changed
        # res = [res]
        print check_domain,res
        res_q.put([check_domain,res,changed])
    print '获取完成...'


def main():

    print 'start:  ', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    # 获取域名
    get_domains()
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



if __name__ == '__main__':
    while True:
        main()
        time.sleep(1800)
    # schedule.every(1).minutes.do(main)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    # main()
