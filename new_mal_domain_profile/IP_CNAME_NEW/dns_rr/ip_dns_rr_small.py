# encoding:utf-8

"""
    使用阿里CNNIC DNS获取域名NS记录，A记录和CNAME记录
    注：每次运行注意更新last_visit_times的数
        循环获取前先测试一下(尤其注意获取成功和不成功时visittimes的变化)


        Temporary failure in name resolution after running for a number of hours
        https://stackoverflow.com/questions/8356517/permanent-temporary-failure-in-name-resolution-after-running-for-a-number-of-h
"""

import DNS
import dns.resolver
import random
import tldextract
import chardet
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

"""获取记录超时时间"""
timeout = 20

"""CNNIC DNS"""
server = '1.2.4.8'


def find_ns(fqdn_domain,resolver,dns_message):
    """
    获取域名的NS名称
    # 获取NS用dns.resolver 从而可以获得ns详细异常信息
    注意：部分是多级NS，所以需要进行两次判断
    """
    ns = []
    ns_ips = []
    domain_len = len(fqdn_domain.split('.')) # 点的个数用来计算能获取几次"次级域名"
    ns_tmp_msg = ''

    for i in range(0,domain_len):
        ns = []
        ns_ip = []
        ns_tmp_msg = ''
        flag = False
        resolver.nameservers = [server]

        for _ in range(2):
            ns_tmp_msg = ''
            # 循环获取2次，如果一次获取成功则break
            try:
                resp = resolver.query(fqdn_domain, 'NS')
                # 从additional中获取ns的A记录
                answers= [answer.to_text() for answer in resp.response.answer]
                ns.extend(get_rr_content(answers))
                additional = [answer.to_text() for answer in resp.response.additional]
                ns_ips.extend(get_rr_content(additional))
                break
            except dns.resolver.NoAnswer, e:
                ns_tmp_msg = 'NS Exception msg:NoAnswer'
            except dns.resolver.NXDOMAIN, e:
                ns_tmp_msg = 'NS Exception msg:NXdomain'
            except dns.resolver.NoNameservers, e:
                ns_tmp_msg = 'NS Exception msg:NoNameservers'
            except dns.resolver.Timeout, e:
                ns_tmp_msg = 'NS Exception msg:Timeout'
            except:
                ns_tmp_msg = 'NS Exception msg: Unexcepted Errors'
            # 其他异常处理由主函数一致处理
        if isinstance(ns,list) and ns:# 说明正常获取到了ns记录
            if ns_tmp_msg:
                dns_message.append(ns_tmp_msg)
            return ns,ns_ips
        else:
            fqdn_domain = extract_main_domain(fqdn_domain)
            domain_tld = tldextract.extract(fqdn_domain)
            # print "提取次级域名为： " + fqdn_domain
            if fqdn_domain == domain_tld.suffix:
                if ns_tmp_msg:
                    dns_message.append(ns_tmp_msg)
                return ns,ns_ips


def get_cname_ip(ns_ips,fqdn_domain,resolver,dns_message):
    """
    获取指定dns记录的内容和ttl时间，主要为A记录和CNAME记录
    """
    cnames,ips = [], []
    cname_tmp_msg = ''
    ip_tmp_msg = ''

    for ns_ip in ns_ips:
        cname_tmp_msg = ''
        ip_tmp_msg = ''
        resolver.nameservers = [ns_ip]
        try:
            resp_CNAME = resolver.query(fqdn_domain, 'CNAME')
            answers= [answer.to_text() for answer in resp_CNAME.response.answer]
            cnames.extend(get_rr_content(answers))
            break
        except dns.resolver.NoAnswer, e:
            cname_tmp_msg = 'CNAME Exception msg:NoAnswer'
        except dns.resolver.NXDOMAIN, e:
            cname_tmp_msg = 'CNAME Exception msg:NXDOMAIN'
        except dns.resolver.NoNameservers, e:
            cname_tmp_msg = 'CNAME Exception msg:NoNameservers'
        except dns.resolver.Timeout, e:
            cname_tmp_msg = 'CNAME Exception msg:Timeout'
        except:
            cname_tmp_msg = 'CNAME Exception msg:Unexcepted Errors'

        try:
            resp_A = resolver.query(fqdn_domain, 'A')
            answers= [answer.to_text() for answer in resp_A.response.answer]
            ips.extend(get_rr_content(answers))
            break
        except dns.resolver.NoAnswer, e:
            ip_tmp_msg = 'A Exception msg:NoAnswer'
        except dns.resolver.NXDOMAIN, e:
            ip_tmp_msg = 'A Exception msg:NXDOMAIN'
        except dns.resolver.NoNameservers, e:
            ip_tmp_msg = 'A Exception msg:NoNameservers'
        except dns.resolver.Timeout, e:
            ip_tmp_msg = 'A Exception msg:Timeout'
        except:
            ip_tmp_msg = 'A Exception msg:Unexcepted Errors'

    if cname_tmp_msg:
        dns_message.append(cname_tmp_msg)
    if ip_tmp_msg:
        dns_message.append(ip_tmp_msg)
    return cnames,ips

def fetch_ip_cnames_handler(fqdn_domain, g_ns, g_ips, g_cnames,resolver,dns_message):
    """
    递归获取域名的cname、cname_ttl和IP、IP_ttl记录
    """

    ns,ns_ips = find_ns(fqdn_domain,resolver,dns_message)  # 得到ns列表
    if not ns:
        return

    if not g_ns:
        # 注意，这里g_ns.extend(ns)实际时代替了g_ns=ns,不知道为什么g_ns=ns最终的g_ns还是空
        g_ns.extend(ns) # g_ns=[]说明时获取fqdn的ns，而不是递归调用此函数时获取的cname的ns

    cname,ips = get_cname_ip(ns_ips,fqdn_domain,resolver,dns_message)
    # 若cname不为空，则递归进行cname的dns记录获取
    if cname and isinstance(cname,list):
        g_cnames.extend(cname)
        return fetch_ip_cnames_handler(cname[-1], g_ns, g_ips, g_cnames,resolver,dns_message)
    elif ips:
        g_ips.extend(ips)


def get_complete_dns_rr(fqdn_domain, g_ns, g_ips, g_cnames,dns_message):

    resolver = dns.resolver.Resolver(configure=False)
    # 获取ip和cname等信息
    fetch_ip_cnames_handler(fqdn_domain, g_ns, g_ips, g_cnames,resolver,dns_message)
    main_domain = tldextract.extract(fqdn_domain).registered_domain
    ns,ns_ips = find_ns(main_domain,resolver, dns_message)

def get_rr_content(answers):
    rr = []
    for record in answers:
        for single_record in record.split('\n'):
            temp = single_record.split(' ')
            rr.append(' '.join(temp[4:]))
    return rr


def extract_main_domain(fqdn_domain):
    """
    获取次级域名
    """
    fqdn = fqdn_domain.split('.')
    fqdn.pop(0)
    main_domain = '.'.join(fqdn)
    return main_domain


if __name__ == '__main__':
    # for _ in range(5):
    g_ns, g_ips, g_cnames,g_soa, g_txt, g_mx, dns_message= [],[],[],[],[],[],[]
    # fetch_rc_ttl('www.000-078-japan.com', g_ns, g_ips, g_cnames)
    get_complete_dns_rr('www.00000040.com', g_ns, g_ips, g_cnames,g_soa, g_txt, g_mx,dns_message)
    print g_ns, g_ips, g_cnames,g_soa, g_txt, g_mx,dns_message
    print '\n'
