#-*- coding:utf-8 -*-
"""
    与whois.cymru.com建立连接获取AS信息
"""
import socket
# import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def get_asn_whois(query_ip):
    '''
    核心函数
    功能： 向whois.cymru.com发出查询，获得ip的AS、ASNAME和管理组织名称asn_registry
    return:完整的AS信息
    '''
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.settimeout(10)
    conn.connect(('38.229.36.122', 43))
    # Query the Cymru whois server, and store the results.
    conn.send((
        ' -r -a -c -p -f {0}{1}'.format(
            query_ip, '\r\n')
    ).encode())

    data = ''
    while True:

        d = conn.recv(4096).decode()
        data += d

        if not d:

            break
    return data



def parse_as_info(asn_whois):
    '''
    解析asn的信息
    '''
    temp = asn_whois.split('|')
    parsed_as_info = {}
    parsed_as_info['ASN'] = temp[0].strip(' \n')
    parsed_as_info['AS_cidr'] = temp[2].strip(' \n')
    parsed_as_info['AS_country_code'] = temp[3].strip(' \n').upper()
    parsed_as_info['RIR'] = temp[4].strip(' \n')
    parsed_as_info['AS_date'] = temp[5].strip(' \n')
    parsed_as_info['AS_owner'] = temp[6].strip(' \n')
    return parsed_as_info

def get_std_asinfo(ip):
    """
    封装获取及解析as信息的函数
    """
    as_info = get_asn_whois(ip)
    std_asinfo = parse_as_info(as_info)
    # std_asinfo['AS_insert_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return std_asinfo


if __name__ == '__main__':
    """
    '38.229.36.122'
    '36.0.0.9'
    """
    pass
