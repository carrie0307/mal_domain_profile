# encoding:utf-8
'''
    功能：根据domain_conn_dm表进行全库的注册团伙发现
    输入可以是域名/注册人姓名/注册邮箱/注册电话/ip/cname/外链域名/键入域名
'''

"""
1 得到第一层关联的域名集合D和注册信息Reg
2 遍历D中每个元素d，得到d关联的第一层域名D1和注册信息Reg (注意 环 的问题)
3 返回：graph_info:
           nodes 每个注册信息结点
           links 描述结点关系
       show_info:列举有哪些注册信息，各关联多少个域名

4 注意：遍历的时候域名不要重复;
       爬取到的注册信息也不要和重复

relative_reginfo_getter = get_relative_reginfo.Relative_reginfo_getter('000000.com')
graph_info,show_info_complete = relative_reginfo_getter.get_relative_data()
print show_info_complete

relative_domain_getter = get_relative_domain.Relative_domain_getter('000000.com')
graph_info,show_info = relative_domain_getter.get_relative_data()

"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import get_relative_reginfo
import get_relative_domain
from Base import Base


class Reg_gang(Base):

    def __init__(self,domain):
        self.domain = domain
        Base.__init__(self)
        self.relative_domains = set()
        self.relative_domains.add(self.domain)
        self.relative_reg_name = set()
        self.relative_reg_email = set()
        self.relative_reg_phone = set()

    def get_relative_data(self,query_domain):
        collection = self.mongo_db['domain_conn_dm_test']
        fetch_data = collection.find({'source_domain':query_domain},{'_id':False,'source_domain':False,'visit_times':False})
        fetch_data = list(fetch_data)[0]

        relative_domains = set()
        relative_reg_name = set()
        relative_reg_email = set()
        relative_reg_phone = set()
        for key in fetch_data:
            if key == 'ip_domains' or key == 'cname_domains':
                for domain,reg_info in zip(fetch_data[key]['domains'],fetch_data[key]['reg_info']):
                    if domain['domain'] != query_domain:
                        relative_domains.add(domain['domain'])
                    if reg_info['reg_info']['reg_name'] != '':
                        relative_reg_name.add(reg_info['reg_info']['reg_name'])
                    if reg_info['reg_info']['reg_email'] != '':
                        relative_reg_email.add(reg_info['reg_info']['reg_email'])
                    if reg_info['reg_info']['reg_phone'] != '':
                        relative_reg_phone.add(reg_info['reg_info']['reg_phone'])
            else:
                for domain,reg_info in zip(fetch_data[key]['domains'],fetch_data[key]['reg_info']):
                    if domain != query_domain:
                        relative_domains.add(domain)
                    if key != 'links_domains':
                        if reg_info['reg_info']['reg_name'] != '':
                            relative_reg_name.add(reg_info['reg_info']['reg_name'])
                        if reg_info['reg_info']['reg_email'] != '':
                            relative_reg_email.add(reg_info['reg_info']['reg_email'])
                        if reg_info['reg_info']['reg_phone'] != '':
                            relative_reg_phone.add(reg_info['reg_info']['reg_phone'])

        relative_domains = list(relative_domains)
        relative_reg_name = list(relative_reg_name)
        relative_reg_email = list(relative_reg_email)
        relative_reg_phone = list(relative_reg_phone)
        return relative_domains,relative_reg_name,relative_reg_email,relative_reg_phone


    def spider_relative_data(self):
        new_domains,new_relative_reg_name,new_relative_reg_email,new_relative_reg_phone = self.get_relative_data(self.domain)
        print new_domains
        print new_relative_reg_name
        print new_relative_reg_email
        print new_relative_reg_phone





if __name__ == '__main__':
    reg_gang_getter = Reg_gang('0-com.com')
    reg_gang_getter.spider_relative_data()
    del reg_gang_getter
