# encoding:utf-8
'''
    功能：前端icp展示数据获取(向get_icp_info函数传入要获取icp信息的域名即可)
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
        return '无'
    else: # 查到重复的情况
        return reuse_check.split(';')


def reuse_icp_domain(domains):
    '''
    功能：对重复icp的域名获取icp信息
    param: domains: 与原域名页面icp重复的域名列表
    return: return_dm_icp: [{'domain':domain,'auth_icp':权威icp,'page_icp':页面icp},{'domain':domain,'auth_icp':auth_icp,'page_icp':page_icp}..]
    '''
    return_dm_icp = []
    for domain in domains:
        sql = "SELECT domain,auth_icp,page_icp FROM domain_icp WHERE domain = '%s';" %(domain)
        fetch_data = mysql_conn.exec_readsql(sql)
        domain,auth_icp,page_icp = fetch_data[0]
        return_dm_icp.append({'domain':domain,'auth_icp':auth_icp,'page_icp':page_icp})
    return return_dm_icp


def get_icp_info(domain):
    '''
    param: domain: 当前要获取icp信息的域名
    return: icp_info: 处理后的icp信息
        icp_info key含义解释
            return: auth_icp: ICP备案
            return: page_icp: 页面ICP信息
            reuse_check:
                      当reuse_check对应value为字符串时，直接显示在"页面相同ICP"一栏中;
                      当reuse_check对应value为字典{'reuse_num':reuse_num,'reuse_domains':return_dm_icp}，'reuse_num'对应内容显示在"页面相同ICP"一栏中，'reuse_domains'显示在点击查看的表格中。
            return: icp_tag:
    '''
    sql = "SELECT auth_icp,page_icp,reuse_check,icp_tag FROM domain_icp WHERE domain = '%s';" %(domain)
    fetch_data = mysql_conn.exec_readsql(sql)
    auth_icp,page_icp,reuse_check,icp_tag = fetch_data[0]
    # print auth_icp,page_icp,reuse_check,icp_tag
    auth_icp = deal_auth_icp(auth_icp)
    page_icp = deal_page_icp(page_icp)
    reuse_check = reuse_check_info(reuse_check)
    if isinstance(reuse_check,list):
        reuse_num = len(reuse_check)
        return_dm_icp = reuse_icp_domain(reuse_check)
        icp_info = {'auth_icp':auth_icp,'page_icp':page_icp,'reuse_check':{'reuse_num':reuse_num,'reuse_domains':return_dm_icp},'icp_tag':icp_tag}
    else:
        icp_info = {'auth_icp':auth_icp,'page_icp':page_icp,'reuse_check':reuse_check,'icp_tag':icp_tag}
    return icp_info


if __name__ == '__main__':
    print get_icp_info('00000z.com')
