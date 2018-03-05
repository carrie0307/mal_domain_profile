# encoding:utf-8
'''
    功能：前端icp展示数据获取(调用ICP_data类的get_icp_info函数即可，具体见main函数示例)
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import mysql_operation
mysql_conn = mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')

from Base import Base

class ICP_data(Base):

    def __init__(self,domain):
        self.domain = domain
        Base.__init__(self)


    def deal_auth_icp(self,auth_icp):
        '''
        功能：把auth_icp处理成要显示的数据
        '''
        if auth_icp == '--':
            return '无备案信息'
        return auth_icp


    def deal_page_icp(self,page_icp):
        '''
        功能：把page_icp处理成要显示的数据
        '''
        if page_icp == '-1':
            return '页面无法访问'
        elif page_icp == '--':
            return '页面未显示icp信息'
        else:
            return page_icp

    def reuse_check_info(self,reuse_check):
        '''
        功能：对页面icp重复的域名进行处理
        '''
        if reuse_check == '未获取到页面ICP':
            return '---'
        elif reuse_check == '未发现重复':
            return '无'
        else: # 查到重复的情况
            return reuse_check.split(';')


    def reuse_icp_domain(self,domains):
        '''
        功能：对重复icp的域名获取icp信息
        param: domains: 与原域名页面icp重复的域名列表
        return: return_dm_icp: [{'domain':domain,'auth_icp':权威icp,'page_icp':页面icp},{'domain':domain,'auth_icp':auth_icp,'page_icp':page_icp}..]
        '''
        return_dm_icp = []
        for domain in domains:
            sql = "SELECT domain,auth_icp,page_icp FROM domain_icp WHERE domain = '%s';" %(domain)
            fetch_data = self.mysql_db.query(sql)
            domain,auth_icp,page_icp = fetch_data[0]['domain'],fetch_data[0]['auth_icp'],fetch_data[0]['page_icp']
            return_dm_icp.append({'domain':domain,'auth_icp':auth_icp,'page_icp':page_icp})
        return return_dm_icp


    def get_icp_info(self):
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
            eg.1 icp_info = {auth_icp:权威icp，page_icp:页面icp，reuse_check:无相同,icp_tag:虚假icp}
            eg.2 icp_info = {auth_icp:权威icp，page_icp:页面icp，reuse_check:{reuse_num:重复数量，reuse_domains:[{domain:--,auth_icp:---,page_icp:---},{domain:--,auth_icp:---,page_icp:---}]},icp_tag:虚假icp}
        '''
        sql = "SELECT auth_icp,page_icp,reuse_check,icp_tag FROM domain_icp WHERE domain = '%s';" %(self.domain)
        fetch_data = self.mysql_db.query(sql)
        # print fetch_data
        if fetch_data:
            auth_icp,page_icp,reuse_check,icp_tag = fetch_data[0]['auth_icp'],fetch_data[0]['page_icp'],fetch_data[0]['reuse_check'],fetch_data[0]['icp_tag']
        # print auth_icp,page_icp,reuse_check,icp_tag
        auth_icp = self.deal_auth_icp(auth_icp)
        page_icp = self.deal_page_icp(page_icp)
        reuse_check = self.reuse_check_info(reuse_check)
        if isinstance(reuse_check,list):
            reuse_num = len(reuse_check)
            return_dm_icp = self.reuse_icp_domain(reuse_check)
            icp_info = {'auth_icp':auth_icp,'page_icp':page_icp,'reuse_check':{'reuse_num':reuse_num,'reuse_domains':return_dm_icp},'icp_tag':icp_tag}
        else:
            icp_info = {'auth_icp':auth_icp,'page_icp':page_icp,'reuse_check':reuse_check,'icp_tag':icp_tag}
        return icp_info


if __name__ == '__main__':
    icp_data_getter = ICP_data('0-dian.com')
    icp_info = icp_data_getter.get_icp_info()
    print icp_info
    print icp_info['icp_tag']
    # print get_icp_info('00000z.com')
