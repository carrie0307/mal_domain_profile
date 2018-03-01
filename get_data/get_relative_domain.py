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
                    nodes:[(domain,conn_type),(domain,conn_type) ...,(domain,conn_type)]
                    links: [
                                {
                                    source: '源域名',
                                    target: '***.com',
                                    name: '***@qq.com ', # 指出具体的关联因素
                                    desc:'通过××关联' # 指出关联的类型
                                },
                                {
                                    source: '源域名',
                                    target: '***.net',
                                    name: '***',
                                    desc:'通过**关联'
                                },
                                ......
                        ]
                    }

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
        # nodes是关联域名与源域名的节点，links表示各节点间的指向关系
        nodes, links,  = [],{}
        nodes.append((self.domain,'---'))

        if fetch_data:
            print fetch_data[0].keys()
            cname_domains = fetch_data[0]['cname_domains']['domains']
            for item in cname_domains:
                # 避免添加重复的点
                if item['domain'] not in links:
                    nodes.append((item['domain'],'cname'))
                    links[item['domain']] = {'source':self.domain,'target':item['domain'],'name':item['conn'],'desc':'CNAME关联'}
                else:
                    # 如果已经记录过，则直接在links中整合关系即可
                    links[item['domain']]['name'] = links[item['domain']]['name'] + '/' + item['conn']
                    # 不同cname关联同一域名时，不要重复添加注释信息(避免“CMAME关联/CNAME关联的情况出现”)
                    if 'CNAME关联' not in links[item['domain']]['desc']:
                        links[item['domain']]['desc'] = links[item['domain']]['desc'] + '/CNAME关联'


            ip_domains = fetch_data[0]['ip_domains']['domains']
            for item in ip_domains:
                # 先判断该关联域名是否已经记录过
                if item['domain'] not in links:
                    nodes.append((item['domain'],'ip'))
                    links[item['domain']] = {'source':self.domain,'target':item['domain'],'name':item['conn'],'desc':'IP关联'}
                else:
                    # 如果已经记录过，则直接在links中整合关系即可
                    links[item['domain']]['name'] = links[item['domain']]['name'] + '/' + item['conn']
                    # 不同IP关联同一域名时，不要重复添加注释信息
                    if 'IP关联' not in links[item['domain']]['desc']:
                        links[item['domain']]['desc'] = links[item['domain']]['desc'] + '/IP关联'

            # print ip_domains
            links_domains = fetch_data[0]['links_domains']['domains']
            for item in links_domains:
                if item not in links:
                    nodes.append((item,'outer_domain'))
                    links[item] = {'source':self.domain,'target':item,'name':'','desc':'链出关联'}
                else:
                    links[item]['desc'] = links[item]['desc'] + '/链出关联'

            reg_name_domains = fetch_data[0]['reg_name_domain']['domains']
            reg_email_domains = fetch_data[0]['reg_email_domain']['domains']
            reg_phone_domains = fetch_data[0]['reg_phone_domain']['domains']
            reg_name = fetch_data[0]['reg_name_domain']['conn']
            reg_email = fetch_data[0]['reg_email_domain']['conn']
            reg_phone = fetch_data[0]['reg_phone_domain']['conn']

            for item in reg_name_domains:
                if item not in links:
                    nodes.append((item,'reg_name'))
                    links[item] = {'source':self.domain,'target':item,'name':reg_name,'desc':'注册姓名关联'}
                else:# 注册姓名关联到的域名都是不同的，因此这里可以直接这样写
                    links[item]['name'] = links[item]['name'] + '/' + reg_name
                    links[item]['desc'] = links[item]['desc'] + '/注册姓名关联'

            for item in reg_email_domains:
                if item not in links:
                    nodes.append((item,'reg_email'))
                    links[item] = {'source':self.domain,'target':item,'name':reg_email,'desc':'注册邮箱关联'}
                else:# 注册邮箱关联到的域名都是不同的，因此这里可以直接这样写
                    links[item]['name'] = links[item]['name'] + '/' + reg_email
                    links[item]['desc'] = links[item]['desc'] + '/注册邮箱关联'

            for item in reg_phone_domains:
                if item not in links:
                    nodes.append((item,'reg_phone'))
                    links[item] = {'source':self.domain,'target':item,'name':reg_phone,'desc':'注册电话关联'}
                else:# 注册电话关联到的域名都是不同的，因此这里可以直接这样写
                    links[item]['name'] = links[item]['name'] + '/' + reg_phone
                    links[item]['desc'] = links[item]['desc'] + '/注册电话关联'

            # 获取所有整合后的关系
            links = links.values()
            # 关联图中信息
            graph_info = {'nodes':nodes,'links':links}

            # 对ip关联域名进行整理
            ip_num_dict = self.deal_ip_domains(ip_domains)
            cname_num_dict = self.deal_cname_domains(cname_domains)

            # 图下方陈列的信息
            show_info = {
                        'reg_name':reg_name,'reg_name_num':len(reg_name_domains),
                        'reg_email':reg_email,'reg_email_num':len(reg_email_domains),
                        'reg_phone':reg_phone,'reg_phone_num':len(reg_phone_domains),
                        'links_domains_num': len(links_domains),
                        'ip_info':ip_num_dict,
                        'cname_info':cname_num_dict
                        }
            # print graph_info,show_info
            # print nodes,links
            return graph_info,show_info
        else:
            return {},{}

    def deal_cname_domains(self,cname_domains):
        '''
        功能：对cname关联到的域名进行处理
        '''
        cname_num_dict = {} # cname关联域名数量字典
        print cname_domains
        for item in cname_domains:
            cname = item['conn']
            if cname not in cname_num_dict:
                cname_num_dict[cname] = 0 # 从0开始计数，不包括本身
            cname_num_dict[cname] += 1

        # print cname_domain_dict
        return cname_num_dict    # cname



    def deal_ip_domains(self,ip_domains):
        '''
        功能：对ip关联到的域名进行处理
        '''
        ip_num_dict = {} # ip关联域名数量字典

        for item in ip_domains:
            ip = item['conn']
            if ip not in ip_num_dict:
                ip_num_dict[ip] = 0 # 从0开始计数，不包括本身
            ip_num_dict[ip] += 1   # QUESTION:对于只能关联到本身的域名，这里统计不到

        # print ip_domain_dict
        # print ip_num_dict
        return ip_num_dict



if __name__ == '__main__':
    # domain = '0000246.com' # ip测试
    # domain = '0-dian.com' # cname测试
    # domain = '0-du.com' # 链接测试
    # 0518jx.com regphone

    relative_domain_getter = Relative_domain_getter('000000.com')
    graph_info,show_info = relative_domain_getter.get_relative_data()
    # print graph_info
    print show_info
    # print graph_info['links']
    # print graph_info
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
