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

reg_name_filter_list = ['private','privacy','protect','service','whois','agent','domain','admin','hidden','yinsi']
reg_email_filter_list = ['private','privacy','protect','service','whois'',admin','domain','admin','yinsi']
reg_phone_filter_list = ['+','+.','+.+86.','CN','NA','null']


class Reg_gang(Base):

    def __init__(self,domain):
        self.domain = domain
        Base.__init__(self)
        self.relative_domains = []
        # 可以理解为待爬取（查询关联关系）域名
        self.relative_domains = [self.domain]
        # self.relative_reg_name = []
        # self.relative_reg_email = []
        # self.relative_reg_phone = []
        self.visited_domains = set()
        self.dm_reg_relationship = {}
        self.nodes = []

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
                    # 这里改成与visited_domains比较
                    if domain['domain'] not in self.visited_domains and domain['domain'] not in self.relative_domains:
                        relative_domains.add(domain['domain'])
                    if reg_info['reg_info']['reg_name'] != '':
                        relative_reg_name.add(reg_info['reg_info']['reg_name'])
                    if reg_info['reg_info']['reg_email'] != '':
                        relative_reg_email.add(reg_info['reg_info']['reg_email'])
                    if reg_info['reg_info']['reg_phone'] != '':
                        relative_reg_phone.add(reg_info['reg_info']['reg_phone'])
            else:
                for domain,reg_info in zip(fetch_data[key]['domains'],fetch_data[key]['reg_info']):
                    if key != 'links_domains':
                        # 外链关联到的域名库中大多没有，因此不进行记录（因为记录后也查不到关联信息）
                        if domain not in self.visited_domains and domain not in self.relative_domains:
                            relative_domains.add(domain)
                        if reg_info['reg_name'] != '':
                            relative_reg_name.add(reg_info['reg_name'])
                        if reg_info['reg_email'] != '':
                            relative_reg_email.add(reg_info['reg_email'])
                        if reg_info['reg_phone'] != '':
                            relative_reg_phone.add(reg_info['reg_phone'])

        relative_domains = list(relative_domains)
        relative_reg_name = list(relative_reg_name)
        relative_reg_email = list(relative_reg_email)
        relative_reg_phone = list(relative_reg_phone)
        return relative_domains,relative_reg_name,relative_reg_email,relative_reg_phone


    def organize_node_relationship(self,new_relative_reg_name,new_relative_reg_email,new_relative_reg_phone,query_domain):
        '''
        功能：整理结点关系
        param:query_domain: 此次用于关联查询的源域名
        param:new_relative_reg_name:当前关联到的注册姓名列表
        param:new_relative_reg_name:当前关联到的注册姓名列表
        param:new_relative_reg_name:当前关联到的注册姓名列表
        '''
        for reg_name in new_relative_reg_name:
            if reg_name not in self.dm_reg_relationship:
                self.nodes.append((reg_name,'reg_name'))
                self.dm_reg_relationship[reg_name] = {'source':query_domain,'target':reg_name,'name':self.domain}

        for reg_email in new_relative_reg_email:
            if reg_email not in self.dm_reg_relationship:
                self.nodes.append((reg_email,'reg_email'))
                self.dm_reg_relationship[reg_email] = {'source':query_domain,'target':reg_email,'name':self.domain}

        for reg_phone in new_relative_reg_phone:
            if reg_phone not in self.dm_reg_relationship:
                self.nodes.append((reg_phone,'reg_phone'))
                self.dm_reg_relationship[reg_phone] = {'source':query_domain,'target':reg_phone,'name':self.domain}

    def filter_invalie_reginfo(self,reg_item,reg_type):
        '''
        功能：判断当前注册信息是否是有效的注册信息，过滤掉隐私保护的通用信息
        param:reg_item:注册信息（reg_name / reg_email）
        param:reg_tppe
        return : True: 有效注册信息
        return : False: 无效注册信息
        '''
        pass


    def spider_relative_data(self):
        # new_domains,new_relative_reg_name,new_relative_reg_email,new_relative_reg_phone = self.get_relative_data(self.domain)
        #
        # self.relative_domains.extend(new_domains)
        # self.relative_reg_name.extend(new_relative_reg_name)
        # self.relative_reg_email.extend(new_relative_reg_email)
        # self.relative_reg_phone.extend(new_relative_reg_phone)
        #
        # self.nodes.append((self.domain,'domain'))
        # # 构建当前域名与注册信息对应关系
        # self.organize_node_relationship(new_relative_reg_name,new_relative_reg_email,new_relative_reg_phone,self.domain)

        counter = 0

        # 然后在数据库中开始循环爬取
        while True:
            if self.relative_domains:
                # 获取当前要继续爬取查询的注册信息的域名
                query_domain = self.relative_domains.pop()
                # counter += 1
                print '当前查询域名: ' + query_domain
                if query_domain not in self.visited_domains:
                    # 将当前域名添加到已爬取过域名的列表
                    self.visited_domains.add(query_domain)
                    # 获取当前域名的关联信息
                    new_domains,new_relative_reg_name,new_relative_reg_email,new_relative_reg_phone = self.get_relative_data(query_domain)
                    print '关联域名: ' + str(len(new_domains))
                    print '关联注册人： ' + str(len(new_relative_reg_name))
                    print '关联注册邮箱： ' + str(len(new_relative_reg_email))
                    print '关联注册电话： ' + str(len(new_relative_reg_phone))
                    # print '\n'
                    self.relative_domains.extend(new_domains)
                    self.relative_domains = list(set(self.relative_domains))
                    print 'relative_domains: ' + str(len(self.relative_domains))
                    print '\n'
                    self.organize_node_relationship(new_relative_reg_name,new_relative_reg_email,new_relative_reg_phone,query_domain)
                    # if counter == 2:
                        # break
            else:
                break


        print self.nodes
        self.dm_reg_relationship = self.dm_reg_relationship.values()
        # print self.dm_reg_relationship
        print len(self.dm_reg_relationship)

        # reg_name_string = ''
        # reg_email_string = ''
        # reg_phone_string = ''
        # for node in self.nodes:
        #     if node[1] == 'reg_name':
        #         reg_name_string = reg_name_string + node[0] + '\n'
        #
        #     if node[1] == 'reg_email':
        #         reg_email_string = reg_email_string + node[0] + '\n'
        #
        #     if node[1] == 'reg_phone':
        #         reg_phone_string = reg_phone_string + node[0] + '\n'
        # with open('reg_name.txt','w') as f:
        #     f.write(reg_name_string)
        #
        # with open('reg_email.txt','w') as f:
        #     f.write(reg_email_string)
        #
        # with open('reg_phone.txt','w') as f:
        #     f.write(reg_phone_string)



if __name__ == '__main__':
    # 0002558.com
    reg_gang_getter = Reg_gang('0002558.com')
    reg_gang_getter.spider_relative_data()
    del reg_gang_getter
