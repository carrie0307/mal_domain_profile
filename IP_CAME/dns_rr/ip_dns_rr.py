# encoding:utf-8

"""
    使用阿里114DNS获取域名NS记录，A记录和CNAME记录
    注：每次运行注意更新last_visit_times的数
        循环获取前先测试一下(尤其注意获取成功和不成功时visittimes的变化)
"""

import DNS
import random
import tldextract

"""获取记录超时时间"""
timeout = 20

"""阿里114DNS"""
server = '114.114.114.114'


def find_ns(fqdn_domain):
    """
    获取域名的NS名称
    注意：部分是多级NS，所以需要进行两次判断
    """
    ns = []
    domain_len = len(fqdn_domain.split('.')) # 点的个数用来计算能获取几次"次级域名"
    for i in range(0,domain_len):
        req_obj = DNS.Request()
        flag = False # 是否获取成功标志，默认为false
    
        # 取消这里的异常捕获，把异常捕获都至于了ge_ip_cname_td函数中统一处理
        for _ in range(3):
            try:
                answer_obj = req_obj.req(name=fqdn_domain, qtype=DNS.Type.NS, server=server, timeout=timeout)
                flag = True
                break
            except:
                continue

        if not flag:# 如果没有获取成功，则再获取一次，这里不加异常处理，若还是获取失败，则直接由get_ip_cname_td进行异常捕获
            answer_obj = req_obj.req(name=fqdn_domain, qtype=DNS.Type.NS, server=server, timeout=timeout)

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
    flag = False # 是否获取成功标志，默认为false
    # try:
    # 取消这里的异常捕获，把异常捕获都至于了ge_ip_cname_td函数中统一处理
    for _ in range(3):
        try:
            answer_obj = req_obj.req(name=domain, qtype=DNS.Type.A, server=ns_name, timeout=timeout)
            flag = True # 标志已经获取成功了
            break
        except:
            continue

    if not flag: # 如果没有获取成功，则再获取一次，这里不加异常处理，若还是获取失败，则直接由get_ip_cname_td进行异常捕获
        answer_obj = req_obj.req(name=domain, qtype=DNS.Type.A, server=ns_name, timeout=timeout)

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


def fetch_rc_ttl(fqdn_domain, g_ns, g_ips, g_cnames):
    """
    递归获取域名的cname、cname_ttl和IP、IP_ttl记录
    """

    # print '正在查询的域名：',fqdn_domain
    ns = find_ns(fqdn_domain)  # 得到ns列表

    # 若无ns，则停止
    if not ns:
        return
    if not g_ns:
        # 注意，这里g_ns.extend(ns)实际时代替了g_ns=ns,不知道为什么g_ns=ns最终的g_ns还是空
        g_ns.extend(ns) # g_ns=[]说明时获取fqdn的ns，而不死递归调用此函数时获取的cname的ns

    ns_name = random.choice(ns)   # 随机选择一个ns服务器
    ip, cname = handle_domain_rc(ns_name, fqdn_domain)  # 得到cname和cname的ttl

    # 若cname不为空，则递归进行cname的dns记录获取
    if cname:
        g_cnames.extend(cname)
        return fetch_rc_ttl(cname[-1], g_ns, g_ips, g_cnames)
    elif ip:
        g_ips.extend(ip)


if __name__ == '__main__':
    g_ns, g_ips, g_cnames= [],[],[]
    # fetch_rc_ttl('www.000-078-japan.com', g_ns, g_ips, g_cnames)
    fetch_rc_ttl('www.0666hg.com', g_ns, g_ips, g_cnames)
    print g_ns, g_ips, g_cnames
    # main()
    # fetch_rc_ttl('0-360c.com')
    # print g_cnames
    # print g_ips
    # print g_ns
