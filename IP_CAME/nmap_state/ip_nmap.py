#-*- coding:utf-8 -*-
"""
    nmap扫描获取主机与80,443端口状态
    学习：http://xiaix.me/python-nmapxiang-jie/
         http://www.tianfeiyu.com/?p=1360
"""
import nmap # 导入 nmap.py 模块
import datetime
'''
baidu.com   111.13.101.208
520820.com  192.5.6.30
365635.com  112.121.172.146
'''


def get_nmap_state(ip):
    """
    核心函数
    param ip:要扫描的ip
    return ip_info={state:主机状态，state80:80端口状态，state443:443端口状态,'status_insert_time':状态探测时间}
    """
    ip_info = {}
    ip_info = {'state80': '0', 'state': '0', 'state443': '0'}
    nm = nmap.PortScanner()
    res = nm.scan(ip,'80,443')
    if res['scan']:
        ip_info['state'] = res['scan'][ip]['status']['state']
        for port in res['scan'][ip]['tcp']:
            ip_info['state'+str(port)] = res['scan'][ip]['tcp'][port]['state']
    ip_info['state_insert_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return ip_info


if __name__ == '__main__':
    ip = '112.121.172.146'
    print get_nmap_state(ip)
