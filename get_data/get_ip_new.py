# encoding:utf-8
'''
    功能：通过get_ip_info函数获取ip分析相关信息

    从mongo数据库中，每次获取最新一次的ip记录
    注：ip变化频率暂时置为了空
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from Base import Base


class newIP_data_getter(Base):

    def __init__(self,domain):
        self.domain = domain
        self.return_data = {}
        Base.__init__(self)
        self.get_data_from_mongo()


    def get_data_from_mongo(self):
        '''
        功能：从mongo数据库获取数据
        '''
        collection = self.mongo_db['domain_ip_cname']
        fetch_data = collection.find({'domain':self.domain},{'_id':False,'change_times':1,'visit_times':1,
                                                                 'domain_ip_cnames':{'$slice':-1}})
        self.fetch_data = list(fetch_data)[0]



    def get_ip_num(self):
        '''
            功能：根据取回的当次数据的得到ip数量
            return: ip_num: 最后一次dns探测所得的ip数量
        '''
        ip_num = len(self.fetch_data['domain_ip_cnames'][0]['ips'])
        self.return_data['ip_num'] = ip_num


    def get_ip_change_frequency(self):
        '''
            功能：根据visit_times chagne_times计算ip变化频率
            change_frequency = change_times / visit_times
        '''
        change_times = self.fetch_data['change_times']
        visit_times = self.fetch_data['visit_times']
        self.return_data['change_frequency'] = str(int(change_times)) + ' / ' + str(int(visit_times))


    def get_table_info(self):
        '''
            功能：组装ip展示列表中的信息：ip,insert_time,ip_state,ip_locate,oper,asn,as_owner
        '''
        self.return_data['table_info'] = []
        domain_ip_cnames = self.fetch_data['domain_ip_cnames'][0]
        for index,ip in enumerate(domain_ip_cnames['ips']):
            temp = {}
            # print ip
            temp['IP'] = ip
            temp['insert_time'] = domain_ip_cnames['insert_time']
            temp['ASN'] = domain_ip_cnames['ip_as'][index]['ASN']
            temp['AS_OWNER'] = domain_ip_cnames['ip_as'][index]['AS_owner']
            temp['oper'] = domain_ip_cnames['ip_geo'][index]['oper']
            temp['geo'] = self.get_ip_locate(domain_ip_cnames['ip_geo'][index])
            temp['state80'] = self.get_ip_state(domain_ip_cnames['ip_state'][index])
            self.return_data['table_info'].append(temp)

    def get_ip_locate(self,ip_geo):
        '''
        功能：从ip的地理位置信息中组装出要显示的ip地理位置信息(get_table_info调用)
        param: ip_geo: mongo中一条ip的地理位置信息(字典形式)
        reutrn: geo: 组装好的ip地理位置信息
        '''
        country = ip_geo['country']
        region = ip_geo['region']
        city = ip_geo['city']
        geo = country

        if country == '香港' or country == '台湾' or country == '内网IP':
            return geo
        elif region != '0':
            geo = geo + '-' + region
        if city != '0' and city != region:
            geo = geo + '-' + city
        return geo


    def get_ip_state(self,ip_state):
        '''
        功能：组装出ip状态信息(get_table_info调用)
        param: ip_state信息 {u'state80': u'open', u'state': u'up', u'state443': u'open'}
        return: ip 80端口的状态信息
        '''
        if ip_state['state80'] == 'open':
            return '80端口-开放'
        elif ip_state['state80'] == 'closed':
            return '80端口-关闭'
        else:
            # 对应filter和没有scan字段的情况(0)
            return '无法探测到'

    def get_soa(self):
        '''
        获取soa记录
         http://www.sigma.me/2011/01/01/about_dns_soa.html

        return:soa_info:[
                         {
                         'MANME':一个域名,
                         'RNAME':一个域名,
                         'retry': 一个字符串,
                         'serial': 一个字符串,
                         'minimum': 一个字符串,
                         'refresh': 一个字符串,
                         'expire': 一个字符串,
                         }
                        ]
        '''

        soa_info = []
        soa = self.fetch_data['domain_ip_cnames'][0]['soa']
        for soa_rr in soa:
            soa_dict = {}
            soa_dict['MNAME'] = soa_rr[0]
            soa_dict['RNAME'] = soa_rr[1]
            for item in soa_rr[2:]:
                content = str(item[1])
                if len(item) == 3:
                    content = content + '  ' + str(item[2])

                soa_dict[item[0]] = content
            soa_info.append(soa_dict)

        return soa_info


    def get_ns(self):
        '''
        功能：获取ns记录
        return:ns_info: [ns1,ns2,...]
        '''
        ns = []
        domain_ip_cnames = self.fetch_data['domain_ip_cnames'][0]
        ns.extend(domain_ip_cnames['NS'])
        return ns


    def get_mx(self):
        '''
        功能：获取MX记录
        return: mx_info
            [
             {'preference': 10(一个数字), 'exchange': u'in1-smtp.messagingengine.com'(一个域名)},
             {'preference': --, 'exchange': --},

            ]
        '''
        mx_info = []
        mx = self.fetch_data['domain_ip_cnames'][0]['mx']
        for mx_rr in mx:
            mx_dict = {}
            mx_dict['preference'] = mx_rr[0]
            mx_dict['exchange'] = mx_rr[1]

            mx_info.append(mx_dict)

        return mx_info


    def get_txt(self):
        '''
        功能：获取txt记录
        return: txt_info:[txt1, txt2,...]
        '''
        txt_info = []
        txt = self.fetch_data['domain_ip_cnames'][0]['txt']
        for txt_rr in txt:
            content = ''
            for item in txt_rr:
                content = content + item + ' '

            txt_info.append(content)

        return txt_info


    def get_cname(self):
        '''
        功能：获取cname记录
        return:cnames:[cname1,cname2,...]
        '''
        cnames = []
        cnames.extend(self.fetch_data['domain_ip_cnames'][0]['cnames'])
        return cnames


    def get_other_dns_rr(self):
        '''
        功能：获取Cname，NS,MX,SOA,TXT记录
        '''
        self.return_data['other_dns_rr'] = {}
        self.return_data['other_dns_rr']['ns'] = self.get_ns()
        self.return_data['other_dns_rr']['mx'] = self.get_mx()
        self.return_data['other_dns_rr']['soa'] = self.get_soa()
        self.return_data['other_dns_rr']['cname'] = self.get_cname()


    def get_data(self):
        '''
        功能：封装以上数据获取函数
        return: self.return_data:
        {
        ip_num: ip数量,
        change_frequency: ip变化频率
        table_info:[
                        {
                            # 第一条ip的信息
                            'oper': '--',       # 运营商
                            'state80': '--',    # 80端口状态
                            'IP':'--',          # IP
                            'AS_OWNER': '--',   # AS拥有者
                            'insert_time': '--',
                            'geo': '--',        # 地理位置
                            'ASN': '--'         # AS编号
                        },
                        {
                            # 第2条ip的信息
                        }

                    ],
        other_dns_rr:
                    {
                    cname:[cname1,cname2,...],
                    ns:[ns1,ns2,...],
                    txt:[txt1,txt2,...],
                    mx:
                        [
                            {
                            'preference': 10(一个数字),  # 优先级
                            'exchange': u'in1-smtp.messagingengine.com'(一个域名)  # 指定愿意充当所有者名称的邮件交换的主机的<域名>。
                            },
                            {},...
                        ],
                    soa:
                        [
                             {
                             'MANME':一个域名,     # 该域的原始或主要数据源的NS
                             'RNAME':一个域名,     # 负责此域的负责人员邮箱
                             'serial': 一个字符串,  # 序列号
                             'refresh': 一个字符串, # 刷新时间间隔
                             'retry': 一个字符串,   # (刷新失败)重试时间间隔
                             'expire': 一个字符串,  # 过期时间
                             'minimum': 一个字符串, # 生存时间
                             },
                             {
                             ...
                             }
                        ]

                    }


        }
        '''
        self.get_ip_num()
        self.get_ip_change_frequency()
        self.get_table_info()
        self.get_other_dns_rr()
        return self.return_data


if __name__ == '__main__':

    ip_getter = newIP_data_getter('00660.com')
    # ip_getter = newIP_data_getter('78567.com')
    print ip_getter.get_data()
