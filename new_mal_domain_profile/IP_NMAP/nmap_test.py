#-*- coding:utf-8 -*-
"""
    nmap扫描获取主机与80,443端口状态
    学习：http://xiaix.me/python-nmapxiang-jie/
         http://www.tianfeiyu.com/?p=1360
         nmap 含义： https://www.jianshu.com/p/069c2cee75b0
         nmap,zmap,masscan比较 http://www.freebuf.com/sectool/119340.html
         nmap入门精讲 http://www.cnblogs.com/st-leslie/p/5115280.html
"""
import nmap # 导入 nmap.py 模块

'''

{'nmap': {'scanstats': {'uphosts': '1', 'timestr': 'Tue Mar 27 16:49:46 2018', 'downhosts': '0', 'totalhosts': '1', 'elapsed': '24.88'}, 'scaninfo': {'tcp': {'services': '22-443', 'method': 'connect'}}, 'command_line': 'nmap -oX - -p 22-443 -sV 220.181.57.216'}, 'scan': {'220.181.57.216': {'status': {'state': 'up', 'reason': 'syn-ack'}, 'hostnames': [{'type': '', 'name': ''}], 'vendor': {}, 'addresses': {'ipv4': '220.181.57.216'}, 'tcp': {80: {'product': 'Apache httpd', 'state': 'open', 'version': '', 'name': 'http', 'conf': '10', 'extrainfo': '', 'reason': 'syn-ack', 'cpe': 'cpe:/a:apache:http_server'}, 443: {'product': 'bfe/1.0.8.18', 'state': 'open', 'version': '', 'name': 'https', 'conf': '10', 'extrainfo': '', 'reason': 'syn-ack', 'cpe': ''}}}}}

80 ['product', 'state', 'version', 'name', 'conf', 'extrainfo', 'reason', 'cpe']

host;protocol;port;name;state;product;extrainfo;reason;version;conf
127.0.0.1;tcp;22;ssh;open;OpenSSH;protocol 2.0;syn-ack;5.9p1 Debian 5ubuntu1;10
127.0.0.1;tcp;25;smtp;open;Exim smtpd;;syn-ack;4.76;10

'''


def get_ip_state(ip):
    '''
    param:ip: @type str 待探测状态的ip
    '''
    ip_info = {}
    nmap_message = ''
    try:
        nm = nmap.PortScanner()
    except nmap.PortScannerError:
        nmap_message = 'NMap Not Found'
        return ip_info,nmap_message

    try:
        res = nm.scan(hosts=ip,arguments='-F -A -Pn ')
        print res
    except Exception,e:
        nmap_message = 'Scan Error: ' + str(e)
        return ip_info,nmap_message

    if res['scan'] and 'tcp' in res['scan'][ip]:
        for port in res['scan'][ip]['tcp']:
            ip_info[port] = res['scan'][ip]['tcp'][port]

    return ip_info, nmap_message



if __name__ == '__main__':
    get_ip_state('103.240.42.10')
