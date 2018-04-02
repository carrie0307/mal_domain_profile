# encoding:utf-8

"""
    使用阿里114DNS获取域名NS记录，A记录和CNAME记录
    注：每次运行注意更新last_visit_times的数
        循环获取前先测试一下(尤其注意获取成功和不成功时visittimes的变化)
"""

import DNS
import random
import tldextract
from datetime import datetime

import sys
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.152','mal_domain_profile')
last_visit_times = 0

"""地理位置相关"""
import ip2region.ip2Region
import ip2region.exec_ip2reg
searcher = ip2region.ip2Region.Ip2Region("ip2region/ip2region.db")

"""获取记录超时时间"""
timeout = 20

"""阿里114DNS"""
server = '114.114.114.114'

## 全局变量
g_cnames = []
g_ips = []
g_ns = []


def find_ns(fqdn_domain):
    """
    获取域名的NS名称
    注意：部分是多级NS，所以需要进行两次判断
    """
    ns = []
    domain_len = len(fqdn_domain.split('.')) # 点的个数用来计算能获取几次"次级域名"
    for i in range(0,domain_len):
        req_obj = DNS.Request()
        try:
            answer_obj = req_obj.req(name=fqdn_domain, qtype=DNS.Type.NS, server=server, timeout=timeout)
        except DNS.Error,e:
            print e
            return []  # 空ns
        for i in answer_obj.answers:
            if i['typename'] == 'NS':
                ns.append(i['data'])
        if ns:
            return ns
        else:
            fqdn_domain = extract_main_domain(fqdn_domain)
            domain_tld = tldextract.extract(fqdn_domain)
            # print "提取次级域名为： " + fqdn_domain
            if fqdn_domain == domain_tld.suffix:
                return ns


def handle_domain_rc(ns_name,domain):
    """
    获取指定dns记录的内容和ttl时间，主要为A记录和CNAME记录
    """
    ip,ip_ttl,cname,cname_ttl = [],[],[],[]
    req_obj = DNS.Request()
    try:
        answer_obj = req_obj.req(name=domain, qtype=DNS.Type.A, server=ns_name, timeout=timeout)
    except DNS.Error, e:
        print '获取域名记录：', e
        return -1, -1

    for i in answer_obj.answers:
        r_data = i['data']
        r_ttl = i['ttl']
        if i['typename'] == 'A':
            ip.append(r_data)
            ip_ttl.append(r_ttl)
        elif i['typename'] == 'CNAME':
            cname.append(r_data)
            cname_ttl.append(r_ttl)
    return ip, cname


def extract_main_domain(fqdn_domain):
    """
    获取次级域名
    """
    fqdn = fqdn_domain.split('.')
    fqdn.pop(0)
    main_domain = '.'.join(fqdn)
    return main_domain


def find_ns_tll(main_domain,ns_name):
    """获取域名NS服务器的默认TTL时间"""
    req_obj = DNS.Request()
    answer_obj = req_obj.req(name=main_domain, qtype=DNS.Type.NS, server=ns_name,timeout=timeout)
    for i in answer_obj.answers:
        if i['typename']=='NS' and i['data'] == ns_name:
            return i['ttl']


def fetch_rc_ttl(fqdn_domain):
    """
    递归获取域名的cname、cname_ttl和IP、IP_ttl记录
    """
    global g_ns
    # print '正在查询的域名：',fqdn_domain
    ns = find_ns(fqdn_domain)  # 得到ns列表

    # 若无ns，则停止
    if not ns:
        return

    g_ns = ns
    ns_name = random.choice(ns)   # 随机选择一个ns服务器
    ip, cname = handle_domain_rc(ns_name, fqdn_domain)  # 得到cname和cname的ttl
    if ip != -1 and cname != -1:
        # 说明获取没有出现异常
        # 若cname不为空，则递归进行cname的dns记录获取
        if cname:
            g_cnames.extend(cname)
            return fetch_rc_ttl(cname[-1])
        elif ip:
            g_ips.extend(ip)


def get_domains(limit_num = None):
    """
    从数据库中获取要初始获取数据的域名
    注：1 last_visit_times 控制这是第几次获取
       2 limit_num 控制是否获取一定量的域名
    """
    global mongo_conn
    global last_visit_times
    domain_list = []

    fetch_data = mongo_conn.mongo_read('domain_ip_cname',{'visit_times':last_visit_times},{'domain':True},limit_num)
    domains = list(fetch_data)
    for domain in domains:
        domain_list.append(domain['domain'])

    return domain_list


def insert_data(check_domain,cnames,ips,ns,ips_geo_list):
    global mongo_conn

    detect_res = {}
    detect_res['cnames'] = cnames
    detect_res['NS'] = ns
    detect_res['ips'] = ips
    detect_res['ip_geo'] = ips_geo_list
    detect_res['insert_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    fetch_data = mongo_conn.mongo_read('domain_ip_cname',{'domain':check_domain},{'visit_times':True},None)
    visit_times = fetch_data[0]['visit_times']
    visit_times += 1

    cur_array = 'domain_ip_cnames.' + str(last_visit_times) # 当前domain_ip_cnames下标

    domain_ip_cnames = mongo_conn.mongo_update('domain_ip_cname',{'domain':check_domain},
                                                {cur_array:detect_res,
                                                'visit_times':visit_times}
                                                )




def main():

    global g_cnames, g_ips, g_ns
    global searcher

    mal_domains = get_domains(50000)

    for check_domain in mal_domains:

        g_cnames, g_ips, g_ns, ips_geo_list = [], [], [], []  # 初始化

        ## 提取domain+tld
        domain_tld = tldextract.extract(check_domain)
        if domain_tld.suffix == "":
            continue
        else:
            check_domain = domain_tld.domain+'.'+domain_tld.suffix

        fqdn_domain = 'www.' + check_domain  # 全域名
        print '查询的域名：',check_domain   # 在查询的域名
        try:
            fetch_rc_ttl(fqdn_domain)
        except Exception,e:
            print str(e)
            continue

        for ip in g_ips:
            # 获取ip地理为值信息
            ip_geo_info = ip2region.exec_ip2reg.get_ip_geoinfo(searcher,ip)
            ips_geo_list.append(ip_geo_info)

        # print g_cnames,g_ips,g_ns,ips_geo_list
        try:
            insert_data(check_domain,g_cnames,g_ips,g_ns,ips_geo_list)
        except Exception,e:
            print str(e)


if __name__ == '__main__':
    # main()
    fetch_rc_ttl('0666p.com')
    print g_cnames
    print g_ips
    print g_ns
