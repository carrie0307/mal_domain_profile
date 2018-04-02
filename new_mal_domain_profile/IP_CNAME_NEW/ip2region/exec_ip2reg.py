#-*- coding:utf-8 -*-
"""
    IP转化地理为值接口
    原作者：https://github.com/lionsoul2014/ip2region
    修改：csy
"""
import struct, sys, os, time
from ip2Region import Ip2Region

"""
    google 216.58.200.46            region 美国|0|0|0|0
    taobao 140.205.220.96           region 中国|华东|上海市|上海市|阿里巴巴
    hitwh.edu.cn 202.102.144.56     region 中国|华东|山东省|威海市|联通
"""


def get_ip_geoinfo(searcher,ip):
    data = searcher.btreeSearch(ip)
    geo_info = data['region'].split('|')
    std_geo_info = dict(country = geo_info[0],
                        region = geo_info[2],
                        city = geo_info[3],
                        oper = geo_info[4])
    return std_geo_info


if __name__ == '__main__':
    searcher = Ip2Region("ip2region.db")
    geo_info = get_ip_geoinfo(searcher,"202.102.144.56")
    for key in geo_info:
        print key,geo_info[key]
