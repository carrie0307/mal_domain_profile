# encoding:utf-8
'''
    功能：获取u干练域名页面数据
    问题：没有添加链入链接的部分
    使用：
         relative_domain_getter = Relative_domain_getter('0-du.com')
         graph_info,show_info = relative_domain_getter.get_relative_data()
         # graph_info,show_info_complete含义在get_relative_data()中有解释
         del relative_domain_getter
    注意：1. 同一域名的同一因素关联到的相同注册信息，只记录一次;
         2  同一域名的不同因素关联到的相同注册信息，在graph_info会在不同关联因素的字典中分别记录;
         3  show_info_complete时对所有注册信息去重后的结果(且注册姓名忽略了大小写 - mysql统计时也自动忽略)
         4  注册信息为空和外链域名无法得到的注册信息，都直接略去，没有进行记录

'''
from __future__ import division
import MySQLdb # 转义使用
import operator # 排序使用
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from Base import Base


class Relative_reginfo_getter(Base):

    def __init__(self,domain):
        self.domain = domain
        self.reg_info_caech = {} # 记录注册信息对应域名数量（缓存）
        Base.__init__(self)


    def get_relative_data(self):
        '''
        功能:从数据库中获取基本的关联域名
        问题：没有添加链入链接的信息
        return: graph_data 关联拓扑图显示的信息
        {
            nodes:[(注册姓名/邮箱/电话，关联类型),(注册姓名/邮箱/电话，关联类型),(注册姓名/邮箱/电话，关联类型)...]
            links:[
                       {
                           source: '源域名',
                           target: '关联到的某个注册信息',
                           name: '***@qq.com ', # 指出具体的关联因素，IP/CNAME/注册姓名/邮箱/电话/outer_domain
                           desc:'通过××关联' # 指出关联的类型
                       },
                       ......
                  ]
        }

        return: show_info_complete 拓扑图下方具体的注册信息及关联域名数量展示
        {
            'reg_name': [{'reg_name':---,'conn_dm_num':n(关联域名数量)},{'reg_name':---,'conn_dm_num':n(关联域名数量)},...],
            'reg_phone': [{'reg_email':---,'conn_dm_num':n(关联域名数量)},{'reg_email':---,'conn_dm_num':n(关联域名数量)},...],
            'reg_email': [{'reg_phone':---,'conn_dm_num':n(关联域名数量)},{'reg_phone':---,'conn_dm_num':n(关联域名数量)},...]
        }

        '''

        graph_info = {} # 拓扑图所显示的信息
        show_info = {'reg_name':[],'reg_email':[],'reg_phone':[]}  # 图下方所显示的注册信息(为show_info_complete作辅助)
        show_info_complete = {'reg_name':[],'reg_email':[],'reg_phone':[]}  # 图下方所显示的信息


        collection = self.mongo_db['domain_conn_dm_test']
        fetch_data = collection.find({'source_domain':self.domain},{'cname_domains.reg_info':True,
                                                                    'ip_domains.reg_info':True,
                                                                    'links_domains.reg_info':True,
                                                                    'reg_name_domain.reg_info':True,
                                                                    'reg_email_domain.reg_info':True,
                                                                    'reg_phone_domain.reg_info':True,
                                                                    'reg_name_domain.conn':True,
                                                                    'reg_email_domain.conn':True,
                                                                    'reg_phone_domain.conn':True})
        # 获取原始数据
        fetch_data = list(fetch_data)

        if fetch_data:
            cname_reg = fetch_data[0]['cname_domains']['reg_info']
            ip_reg = fetch_data[0]['ip_domains']['reg_info']
            links_reg = fetch_data[0]['links_domains']['reg_info']
            reg_name_reginfo = fetch_data[0]['reg_name_domain']['reg_info']
            reg_email_reginfo = fetch_data[0]['reg_email_domain']['reg_info']
            reg_phone_reginfo = fetch_data[0]['reg_phone_domain']['reg_info']
            reg_name = fetch_data[0]['reg_name_domain']['conn']
            reg_email = fetch_data[0]['reg_email_domain']['conn']
            reg_phone = fetch_data[0]['reg_phone_domain']['conn']

            # nodes是关联注册信息与源域名的节点，links表示各节点间的指向关系
            nodes,links = [],{}
            nodes.append((self.domain,'---'))

            # 对cname关联域名的注册信息进行整理
            self.deal_ip_cname_nodes_links(nodes,links,cname_reg,'cname') # 整理nodes和links的内容
            cname_reg_dict = self.deal_cname_reginfo(cname_reg)
            for cname in cname_reg_dict:
                self.add_showinfo_reg(show_info,show_info_complete,cname_reg_dict[cname])

            # 对ip关联域名的注册信息进行整理
            self.deal_ip_cname_nodes_links(nodes,links,ip_reg,'ip') # 整理nodes和links的内容
            ip_reg_dict = self.deal_ip_reginfo(ip_reg)
            for ip in ip_reg_dict:
                self.add_showinfo_reg(show_info,show_info_complete,ip_reg_dict[ip])

            # 对链接的关联域名注册信息进行整理
            self.deal_links_nodes_links(nodes,links,links_reg,'outer_domain') # 整理nodes和links的内容
            link_reg_dict = self.deal_links_reg(links_reg)
            self.add_showinfo_reg(show_info,show_info_complete,link_reg_dict)

            # 对注册信息反查域名所得注册信息进行整理
            reg_name_regdict = self.deal_reginfo_reg(reg_name,reg_name_reginfo) # 整理nodes和links的内容
            self.deal_reginfo_nodes_links(nodes,links,reg_name_reginfo,reg_name,'reg_name')
            self.add_showinfo_reg(show_info,show_info_complete,reg_name_regdict)

            self.deal_reginfo_nodes_links(nodes,links,reg_email_reginfo,reg_email,'reg_email') # 整理nodes和links的内容
            reg_email_regdict = self.deal_reginfo_reg(reg_email,reg_email_reginfo)
            self.add_showinfo_reg(show_info,show_info_complete,reg_email_regdict)

            self.deal_reginfo_nodes_links(nodes,links,reg_phone_reginfo,reg_phone,'reg_phone') # 整理nodes和links的内容
            reg_phone_regdict = self.deal_reginfo_reg(reg_phone,reg_phone_reginfo)
            self.add_showinfo_reg(show_info,show_info_complete,reg_phone_regdict)

            # 根据数量进行排序
            show_info_complete['reg_name'] = sorted(show_info_complete['reg_name'], key=operator.itemgetter('conn_dm_num'), reverse = True)
            show_info_complete['reg_email'] = sorted(show_info_complete['reg_email'], key=operator.itemgetter('conn_dm_num'), reverse = True)
            show_info_complete['reg_phone'] = sorted(show_info_complete['reg_phone'], key=operator.itemgetter('conn_dm_num'), reverse = True)

            links = links.values()
            # 关联图中信息
            graph_info = {'nodes':nodes,'links':links}

            return graph_info,show_info_complete


    def deal_cname_reginfo(self,cname_reg):
        '''
        功能：对cname关联到的域名进行处理
        return: cname_reg_dict
            {
                cname1: {'reg_name': [name1,name2,...], 'reg_phone': [phone1,phone2.,,,], 'reg_email': [email1,email2,...]},
                cname2: {'reg_name': [name1,name2,...], 'reg_phone': [phone1,phone2.,,,], 'reg_email': [email1,email2,...]},
                ...
                cnamen:{}
            }
        '''
        cname_reg_dict = {} # cname关联域名的字典

        for item in cname_reg:
            cname = item['conn']
            reg_info = item['reg_info']

            if cname not in cname_reg_dict:
                cname_reg_dict[cname] = {'reg_name':[],'reg_email':[],'reg_phone':[]}

            # 为空的注册信息不进行记录
            # 同一ip关联到的注册信息只记录一次
            if reg_info['reg_name'] != '' and reg_info['reg_name'] not in cname_reg_dict[cname]['reg_name']:
                cname_reg_dict[cname]['reg_name'].append(reg_info['reg_name'])
            if reg_info['reg_email'] != '' and reg_info['reg_email'] not in cname_reg_dict[cname]['reg_email']:
                cname_reg_dict[cname]['reg_email'].append(reg_info['reg_email'])
            if reg_info['reg_email'] != '' and reg_info['reg_phone'] not in cname_reg_dict[cname]['reg_phone']:
                cname_reg_dict[cname]['reg_phone'].append(reg_info['reg_phone'])

        # print cname_reg_dict
        return cname_reg_dict    # cname


    def deal_ip_reginfo(self,ip_reg):
        '''
        功能：对ip关联到的域名进行处理
        return ip_reg_dict
            {
                ip1: {'reg_name': [name1,name2,...], 'reg_phone': [phone1,phone2.,,,], 'reg_email': [email1,email2,...]},
                ip2: {'reg_name': [name1,name2,...], 'reg_phone': [phone1,phone2.,,,], 'reg_email': [email1,email2,...]},
                ...
                ipn:{}
            }
        '''
        ip_reg_dict = {} # ip关联注册信息的字典

        for item in ip_reg:
            ip = item['conn']
            reg_info = item['reg_info']

            if ip not in ip_reg_dict:
                ip_reg_dict[ip] = {'reg_name':[],'reg_email':[],'reg_phone':[]}

            # 为空的注册信息不进行记录
            # 同一ip关联到的注册信息只记录一次
            if reg_info['reg_name'] != '' and reg_info['reg_name'] not in ip_reg_dict[ip]['reg_name']:
                ip_reg_dict[ip]['reg_name'].append(reg_info['reg_name'])
            if reg_info['reg_email'] != '' and reg_info['reg_email'] not in ip_reg_dict[ip]['reg_email']:
                ip_reg_dict[ip]['reg_email'].append(reg_info['reg_email'])
            if reg_info['reg_email'] != '' and reg_info['reg_phone'] not in ip_reg_dict[ip]['reg_phone']:
                ip_reg_dict[ip]['reg_phone'].append(reg_info['reg_phone'])

        # print ip_reg_dict
        return ip_reg_dict

    def deal_links_reg(self,reginfo_list):
        '''
        功能：对链接域名的注册信息进行处理
        return: link_reg_dict:
            {
                'reg_name':[name1,name2,...],
                'reg_email':[email1,email2,...],
                'reg_phone':[phone1,phone2,...]
            }
        '''
        link_reg_dict = {'reg_name':[],'reg_email':[],'reg_phone':[]}

        for item in reginfo_list:

            # 没有查到注册信息的跳过，不进行处理
            # 只有链接关联的域名才有这种情况
            if item['reg_name'] == '库中暂无该注册信息':
                continue

            if item['reg_name'] != '' and item['reg_name'] not in link_reg_dict['reg_name']:
                link_reg_dict['reg_name'].append(item['reg_name'])

            if item['reg_email'] != '' and item['reg_email'] not in link_reg_dict['reg_email']:
                link_reg_dict['reg_email'].append(item['reg_email'])

            if item['reg_phone'] != '' and item['reg_phone'] not in link_reg_dict['reg_phone']:
                link_reg_dict['reg_phone'].append(item['reg_phone'])

        # print link_reg_dict
        return link_reg_dict

    def deal_reginfo_reg(self,reg_item,reginfo_list):
        '''
        功能：对注册信息关联所得新域名的注册信息进行整理
        param: reg_item: 具体的注册姓名/邮箱/电话
        param: reginfo_list:该reg_item关联所得的注册信息列表[{reg_name:--,reg_email:--,reg_phone:--},{reg_name:--,reg_email:--,reg_phone:--},...]
        return: reg_item_reg:
                {
                reg_name:[name1,name2,...],
                reg_email:[email1,email2,...],
                reg_phone:[phone1,phone2,...]
                }
        '''
        reg_item_reg = {'reg_name':[],'reg_email':[],'reg_phone':[]}

        if reg_item == '': # 注册信息为空的，直接返回
            return reg_item_reg

        for item in reginfo_list:

            # 与源注册信息相同的注册信息不记录
            # 为空的注册信息不记录
            # 重复的注册信息不记录
            # 注册姓名忽略大小写，eg 0000666.com 关联得到的ZHANG SAN,Zhang San,zhang san，在domain_whois中不同，但统计时mysql忽略了大小写，因此这里也忽略
            if item['reg_name'].lower() != reg_item.lower() and item['reg_name'] != '' and item['reg_name'] not in reg_item_reg['reg_name']:
                reg_item_reg['reg_name'].append(item['reg_name'])

            if item['reg_email'] != reg_item and item['reg_email'] != '' and item['reg_email'] not in reg_item_reg['reg_email']:
                reg_item_reg['reg_email'].append(item['reg_email'])

            if item['reg_phone'] != reg_item and item['reg_phone'] != '' and item['reg_phone'] not in reg_item_reg['reg_phone']:
                reg_item_reg['reg_phone'].append(item['reg_phone'])

        return reg_item_reg


    def query_reg_conn_dmnum(self,reg_item):
        '''
        功能：查询某个注册信息关联到的域名数量
        param: reg_item: 具体的注册信息
        '''
        reg_item = MySQLdb.escape_string(reg_item) # 转义
        sql = "SELECT domain_count FROM reg_info WHERE item = '%s';" %(reg_item)
        fetch_data = self.mysql_db.query(sql)
        if fetch_data:# 如果查询到具体的关联数量
            return int(fetch_data[0]['domain_count'])
        else:
            return '尚未统计'


    def add_showinfo_reg(self,show_info,show_info_complete,conn_regdict):
        '''
        功能：向show_info字典中添加关联到的所有注册信息
        '''
        for reg_name in conn_regdict['reg_name']:
            # 注册姓名忽略大小写，eg 0000666.com 关联得到的ZHANG SAN,Zhang San,zhang san，在domain_whois中不同，但统计时mysql忽略了大小写，因此这里也忽略
            if reg_name.lower() not in show_info['reg_name']:
                conn_dm_num = self.query_reg_conn_dmnum(reg_name)
                show_info['reg_name'].append(reg_name.lower())
                show_info_complete['reg_name'].append({'reg_name':reg_name,'conn_dm_num':conn_dm_num})

        for reg_email in conn_regdict['reg_email']:
            if reg_email not in show_info['reg_email']:
                conn_dm_num = self.query_reg_conn_dmnum(reg_email)
                show_info['reg_email'].append(reg_email)
                show_info_complete['reg_email'].append({'reg_email':reg_email,'conn_dm_num':conn_dm_num})

        for reg_phone in conn_regdict['reg_phone']:
            if reg_phone not in show_info['reg_phone']:
                conn_dm_num = self.query_reg_conn_dmnum(reg_phone)
                show_info['reg_phone'].append(reg_phone)
                show_info_complete['reg_phone'].append({'reg_phone':reg_phone,'conn_dm_num':conn_dm_num})

    def deal_ip_cname_nodes_links(self,nodes,links,conn_reg,conn_type):
        """
        功能：ip,cname关联到的注册信息整理到Nodes和links
        param: nodes: 总的nodes结点列表
        param: links: 所有结点的关系字典
        param: conn_reg:进行处理的关联到的注册信息列表
        param: conn_type: 关联元素的类型CNAME/IP
        return: nodes，links的值会改变，因此不进行返回
        """
        if conn_type == 'cname':
            conn_type_info = 'CNAME关联'
        else:
            conn_type_info = 'IP关联'
        for item in conn_reg:
            if item['reg_info']['reg_name'] != '':
                if item['reg_info']['reg_name'] not in links:
                    nodes.append((item['reg_info']['reg_name'],conn_type))
                    links[item['reg_info']['reg_name']] = {'source':self.domain,'target':item['reg_info']['reg_name'],'name':item['conn'],'desc':conn_type_info}
                elif item['conn'] not in links[item['reg_info']['reg_name']]['name']:
                    links[item['reg_info']['reg_name']]['name'] = links[item['reg_info']['reg_name']]['name'] + '/' + item['conn']
                elif conn_type_info not in links[item['reg_info']['reg_name']]['desc']:
                    links[item['reg_info']['reg_name']]['desc'] = links[item['reg_info']['reg_name']]['desc'] + '/' + conn_type_info

            if item['reg_info']['reg_email'] != '':
                if item['reg_info']['reg_email'] not in links:
                    nodes.append((item['reg_info']['reg_email'],conn_type))
                    links[item['reg_info']['reg_email']] = {'source':self.domain,'target':item['reg_info']['reg_email'],'name':item['conn'],'desc':conn_type_info}
                elif item['conn'] not in links[item['reg_info']['reg_email']]['name']:
                    links[item['reg_info']['reg_email']]['name'] = links[item['reg_info']['reg_email']]['name'] + '/' + item['conn']
                elif conn_type_info not in links[item['reg_info']['reg_email']]['desc']:
                    links[item['reg_info']['reg_email']]['desc'] = links[item['reg_info']['reg_email']]['desc'] + '/' + conn_type_info

            if item['reg_info']['reg_phone'] != '':
                if item['reg_info']['reg_phone'] not in links:
                    nodes.append((item['reg_info']['reg_phone'],conn_type))
                    links[item['reg_info']['reg_phone']] = {'source':self.domain,'target':item['reg_info']['reg_phone'],'name':item['conn'],'desc':conn_type_info}
                elif item['conn'] not in links[item['reg_info']['reg_phone']]['name']:
                    links[item['reg_info']['reg_phone']]['name'] = links[item['reg_info']['reg_phone']]['name'] + '/' + item['conn']
                elif conn_type_info not in links[item['reg_info']['reg_phone']]['desc']:
                    links[item['reg_info']['reg_phone']]['desc'] = links[item['reg_info']['reg_phone']]['desc'] + '/' + conn_type_info

    def deal_reginfo_nodes_links(self,nodes,links,conn_reg,conn_item,conn_type):
        '''
        功能：reg_name,reg_phone,reg_email关联到的注册信息整理到Nodes和links
        param: nodes: 总的nodes结点列表
        param: links: 所有结点的关系字典
        param: conn_reg:进行处理的关联到的注册信息列表
        param: conn_item: 具体的关联元素：注册姓名/注册邮箱/注册电话
        paran: conn_type: 关联元素类型：reg_name/reg_email/reg_phone
        return: nodes，links的值会改变，因此不进行返回
        '''
        if conn_type == 'reg_name':
            conn_type_info = '注册姓名关联'
        elif conn_type == 'reg_email':
            conn_type_info = '注册邮箱关联'
        else:
            conn_type_info = '注册电话关联'
        for item in conn_reg:

            if item['reg_name'] != '':
                if item['reg_name'] not in links:
                    nodes.append((item['reg_name'],conn_type))
                    links[item['reg_name']] = {'source':self.domain,'target':item['reg_name'],'name':conn_item,'desc':conn_type_info}
                elif conn_item not in links[item['reg_name']]['name']:
                    links[item['reg_name']]['name'] = links[item['reg_name']]['name'] + '/' + conn_item
                elif conn_type_info not in links[item['reg_name']]['desc']:
                    links[item['reg_name']]['desc'] = links[item['reg_name']]['desc'] + '/' + conn_type_info

            if item['reg_email'] != '':
                if item['reg_email'] not in links:
                    nodes.append((item['reg_email'],conn_type))
                    links[item['reg_email']] = {'source':self.domain,'target':item['reg_email'],'name':conn_item,'desc':conn_type_info}
                elif conn_item not in links[item['reg_email']]['name']:
                    links[item['reg_email']]['name'] = links[item['reg_email']]['name'] + '/' + conn_item
                elif conn_type_info not in links[item['reg_email']]['desc']:
                    links[item['reg_email']]['desc'] = links[item['reg_email']]['desc'] + '/' + conn_type_info

            if item['reg_phone'] != '':
                if item['reg_phone'] not in links:
                    nodes.append((item['reg_phone'],conn_type))
                    links[item['reg_phone']] = {'source':self.domain,'target':item['reg_phone'],'name':conn_item,'desc':conn_type_info}
                elif conn_item not in links[item['reg_phone']]['name']:
                    links[item['reg_phone']]['name'] = links[item['reg_phone']]['name'] + '/' + conn_item
                elif conn_type_info not in links[item['reg_phone']]['desc']:
                    links[item['reg_phone']]['desc'] = links[item['reg_phone']]['desc'] + '/' + conn_type_info


    def deal_links_nodes_links(self,nodes,links,links_reg,conn_type):
        '''
        功能：内外链接关联到的注册信息整理到Nodes和links
        param: nodes: 总的nodes结点列表
        param: links: 所有结点的关系字典
        param: conn_reg:进行处理的关联到的注册信息列表
        paramz: conn_type: 关联元素类型(outer_domain/inner_domain)
        return: nodes，links的值会改变，因此不进行返回
        '''
        if conn_type == 'outer_domain':
            conn_type_info = '外链关联'
        else:
            conn_type_info = '链入关联'
        for item in links_reg:
            if item['reg_name'] != '':
                if item['reg_name'] not in links:
                    nodes.append((item['reg_name'],conn_type))
                    links[item['reg_name']] = {'source':self.domain,'target':item['reg_name'],'name':'','desc':conn_type_info}
                elif conn_type_info not in links[item['reg_name']]['desc']:
                    links[item['reg_name']]['desc'] = links[item['reg_name']]['desc'] + '/' + conn_type_info


if __name__ == '__main__':
    # domain = '0000246.com' # ip测试
    # domain = '0-dian.com' # cname测试
    # domain = '00003499.com' # cname测试
    # domain = '0-du.com' # 链接测试
    # domain = '0-chat.com' # 注册姓名测算
    # 0000666.com
    relative_reginfo_getter = Relative_reginfo_getter('000000.com')
    graph_info,show_info_complete = relative_reginfo_getter.get_relative_data()
    del relative_reginfo_getter
    # print graph_info
    # print show_info_complete
