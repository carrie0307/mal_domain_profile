# encoding:utf-8
'''
    功能：获取u干练域名页面数据
    问题：没有添加链入链接的部分
    注意：同一source_domain的不同元素如果关联到了相同的域名，则都会记录(因此最后关联域名有重复的 -- 在图中分属于不同关联因素)
    使用：
         relative_domain_getter = Relative_domain_getter('0-du.com')
         graph_info,show_info = relative_domain_getter.get_relative_data()
         # graph_info,show_info含义在get_relative_data()中有解释
         del relative_domain_getter

'''
from __future__ import division
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from Base import Base


class Relative_domain_getter(Base):

    def __init__(self,domain):
        self.domain = domain
        Base.__init__(self)


    def get_relative_data(self):
        '''
        功能:从数据库中获取基本的关联域名

        return: graph_data: 可视化拓扑图中信息
                            {
                             'cname_domains': {cname1:[dm1,dm2...],cname2:[dm1,dm2,...]},
                              'ip_domains': {ip1:[dm1,dm2...],ip2:[dm1,dm2,...]},
                              'reg_phone_domains': {reg_phone: [dm1,dm2...]},
                              'reg_name_domains': {reg_name: [dm1,dm2...]},
                              'reg_email_domains':{reg_email:[dm1,dm2,...]}
                              'links_domains': [dm1,dm2,...],
                            }
                show_info: 拓扑图下方展示的信息
                            {
                            'reg_name':reg_name,'reg_name_num':n, # reg_name对应域名数量
                            'reg_email':reg_email,'reg_email_num':m, # reg_email对应域名数量
                            'reg_phone':reg_phone,'reg_phone_num':k, # reg_phone对应域名数量
                            'links_domains_num': p, # 链出关联域名数量
                            'ip_info':ip_domain_dict # ip数量字典:{IP1:n,IP2:n,...}
                            }
        问题：没有添加链入链接的信息
        '''
        # self.mongo_db = MongoClient('172.29.152.151',27017).mal_domain_profile
        collection = self.mongo_db['domain_conn_dm_test']
        fetch_data = collection.find({'source_domain':self.domain},{'cname_domains.domains':True,
                                                                    'ip_domains.domains':True,
                                                                    'links_domains.domains':True,
                                                                    'reg_name_domain.domains':True,
                                                                    'reg_email_domain.domains':True,
                                                                    'reg_phone_domain.domains':True,
                                                                    'reg_name_domain.conn':True,
                                                                    'reg_email_domain.conn':True,
                                                                    'reg_phone_domain.conn':True})
        fetch_data = list(fetch_data)

        if fetch_data:
            cname_domains = fetch_data[0]['cname_domains']['domains']
            ip_domains = fetch_data[0]['ip_domains']['domains']
            links_domains = fetch_data[0]['links_domains']['domains']
            reg_name_domains = fetch_data[0]['reg_name_domain']['domains']
            reg_email_domains = fetch_data[0]['reg_email_domain']['domains']
            reg_phone_domains = fetch_data[0]['reg_phone_domain']['domains']
            reg_name = fetch_data[0]['reg_name_domain']['conn']
            reg_email = fetch_data[0]['reg_email_domain']['conn']
            reg_phone = fetch_data[0]['reg_phone_domain']['conn']

            # 对ip和cname关联域名进行整理
            cname_domain_dict = self.deal_cname_domains(cname_domains)
            ip_domain_dict,ip_num_dict = self.deal_ip_domains(ip_domains)

            # 关联图中信息
            graph_info = {'reg_name_domains':{reg_name:reg_name_domains},
                          'reg_email_domains':{reg_email:reg_email_domains},
                          'reg_phone_domains':{reg_phone:reg_phone_domains},
                          'ip_domains':ip_domain_dict,
                          'cname_domains':cname_domain_dict,
                          'links_domains':links_domains
                          }
            # 图下方陈列的信息
            show_info = {
                        'reg_name':reg_name,'reg_name_num':len(reg_name_domains),
                        'reg_email':reg_email,'reg_email_num':len(reg_email_domains),
                        'reg_phone':reg_phone,'reg_phone_num':len(reg_phone_domains),
                        'links_domains_num': len(links_domains),
                        'ip_info':ip_domain_dict
                        }
            print graph_info,show_info
            return graph_info,show_info
        else:
            return {},{}
            # ip_domain_dict
            # print reg_name_domains
            # print reg_phone_domains
            # print reg_email_domains
            # print reg_name
            # print reg_email
            # print reg_phone


    def deal_cname_domains(self,cname_domains):
        '''
        功能：对cname关联到的域名进行处理
        '''
        cname_domain_dict = {} # cname关联域名的字典

        for item in cname_domains:
            cname = item['conn']
            domain = item['domain']
            cname_domain_dict.setdefault(cname, []).append(domain)

        # print cname_domain_dict
        return cname_domain_dict    # cname


    def deal_ip_domains(self,ip_domains):
        '''
        功能：对ip关联到的域名进行处理
        '''
        ip_domain_dict = {} # ip关联域名的字典
        ip_num_dict = {} # ip关联域名数量字典

        for item in ip_domains:
            ip = item['conn']
            domain = item['domain']
            ip_domain_dict.setdefault(ip, []).append(domain)

            if ip not in ip_num_dict:
                ip_num_dict[ip] = 0 # 从0开始计数，不包括本身
            ip_num_dict[ip] += 1   # QUESTION:对于只能关联到本身的域名，这里统计不到

        # print ip_domain_dict
        # print ip_num_dict
        return ip_domain_dict,ip_num_dict



if __name__ == '__main__':
    # domain = '0000246.com' # ip测试
    # domain = '0-dian.com' # cname测试
    # domain = '0-du.com' # 链接测试
    relative_domain_getter = Relative_domain_getter('0-360c.com')
    graph_info,show_info = relative_domain_getter.get_relative_data()

    # from pymongo import MongoClient
    # mongo_db = MongoClient('172.29.152.151',27017).mal_domain_profile
    # collection = mongo_db['domain_conn_dm_test']
    # domains = list(collection.find({},{'_id':False,'source_domain':True}).limit(100))
    # for domain in domains:
    #     domain = domain['source_domain']
    #     relative_domain_getter = Relative_domain_getter(domain)
    #     graph_info,show_info = relative_domain_getter.get_relative_data()
    #     # relative_domain_getter.get_relative_data()
    #     del relative_domain_getter
    #     print graph_info
    #     print show_info
    #     print '\n'
