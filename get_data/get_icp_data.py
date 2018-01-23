# encoding:utf-8
'''
    功能：前端icp展示数据获取
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import mysql_operation

mysql_conn = mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')


def deal_auth_icp(auth_icp):
    '''
    功能：把auth_icp处理成要显示的数据
    '''
    if auth_icp == '--':
        return '无备案信息'
    return auth_icp


def deal_page_icp(page_icp):
    '''
    功能：把page_icp处理成要显示的数据
    '''
    if page_icp == '-1':
        return '页面无法访问'
    elif page_icp == '--':
        return '页面未显示icp信息'
    else:
        return page_icp

def reuse_check_info(reuse_check):
    '''
    功能：对页面icp重复的域名进行处理
    '''
    if reuse_check == '未获取到页面ICP':
        return '---'
    elif reuse_check == '未发现重复':
        return '无重复ICP'
    else: # 查到重复的情况
        return reuse_check.split(';')


domain = '0-360c.com'
sql = "SELECT auth_icp,page_icp,reuse_check,icp_tag FROM domain_icp WHERE domain = '%s';" %(domain)
fetch_data = mysql_conn.exec_readsql(sql)
auth_icp,page_icp,reuse_check,icp_tag = fetch_data[0]
print auth_icp,page_icp,reuse_check,icp_tag
auth_icp = deal_auth_icp(auth_icp)
page_icp = deal_page_icp(page_icp)
reuse_check = reuse_check_info(reuse_check)
print auth_icp,page_icp,reuse_check,icp_tag
