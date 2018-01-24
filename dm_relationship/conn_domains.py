# encoding:utf-8
'''
    功能：根据各类信息，填充domain_conn_dm表，即每个域名第一层关联到的表
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
import database.mysql_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.151','mal_domain_profile')
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')
import time


# QUESTION:建域名注册信息库 (whois信息库添加触发器，每次添加新的whois信息，向关系库中添加 -- 暂时先没做这个出发器，目前是做全表扫描)
# TODO:以后考虑给relationship表加一个标志位，表示该关系是否已经整理过 （每次更新relationship表时加NEW或OLD）
# TODO： 添加标志位与规则 (规则写文档，尤其是什么时候更新已整理过的标志位)
# TODO: 每次更新关系表时，重复的记录on duplicate key将scan_flag置为old （还是每次执行完这份代码，将所有的scan_flag直接置为old？）
# TODO： links表如何区分（加标志位）

# TODO:缺links的更新
# TODO:却标志位更新方式确定  s所有信息跑完后统一置吧～～～(代码还没写)
# QUESTION: Visit-times先手动置书了(用inc又得多一次查询阿。。。。。)

"""
注意：ip，cname每次都根据relationship表的标志位获取未处理过的关系，因此是put
     注册信息方面：随着域名数量增加，关联域名与注册信息会增多，因此是push(怎么区分是已关联过的还未关联过的？？？)
     连接方面：也是无法区分是否是关联过的
"""

# source_domain = '77360022.cc' # 测试ip 1.32.208.43 /cname
# source_domain = '383088.com'  # 测试注册信息 KAI LI WANG	YUMING3088@GMAIL.COM	+86.18030573226	13
# source_domain = '01iii.com'	 #  测试注册信息  KAP MUI MUI	AXETOP@GMAIL.COM	+1.1940044567	5

class Domain_conn(object):

    def __init__(self,source_domain):
        """
        param: *args: 要构建域名关联关系的source_domain

        """
        # 初始化（根据输入的域名自动执行函数）
        self.source_domain = source_domain
        self.reg_info_cache = {} # 每个域名的关联域名有很多重复，因此设置一个注册信息缓存，对已获取注册信息的域名直接从缓存获取信息
        self.relative_domains_flag = [] # 关联域名标志位处理([{domain:--,relative_domain_flag:[True,...,True]}])
        self.get_conn_domains()


    def get_reg_info(self,domain):
        """
        根据域名获取其注册信息(先查看本地缓存，若有则直接获取，否则查库)
        parar: domain:要查询注册信息的域名
        return reg_info:{'reg_name':--,'reg_email':--,'reg_phone':--}
        """
        global mysql_conn

        if domain in self.reg_info_cache:
            return self.reg_info_cache[domain]
        sql = "SELECT reg_name,reg_email,reg_phone FROM domain_reg_relationship WHERE domain = '%s';" %(domain)
        fetch_data = mysql_conn.exec_readsql(sql)
        if fetch_data: # 库中可以查到该域名的注册信息
            reg_name,reg_email,reg_phone = fetch_data[0]
        else: # 尚未入库域名
            reg_name,reg_email,reg_phone = '库中暂无该注册信息','库中暂无该注册信息','库中暂无该注册信息'
        # 更新缓存
        self.reg_info_cache[domain] = {'reg_name':reg_name,'reg_email':reg_email,'reg_phone':reg_phone}
        # QUESTION:注册信息为空时，照常返回（但是不用为空的注册信息去关联新的域名）
        return {'reg_name':reg_name,'reg_email':reg_email,'reg_phone':reg_phone}


    def get_domains_from_reg(self,reg_type,reg_info):
        """
        功能：根据注册信息获取域名
        param: reg_type: 注册信息类型(reg_name,reg_email,reg_phone)
        param: reg_info: 具体的注册信息(一个域名的注册姓名或邮箱或电话)
        return: domains: 关联到的域名集合
        """
        global mysql_conn
        reg_info = mysql_conn.escate_string(reg_info)
        domains = []
        sql = "SELECT domain FROM domain_reg_relationship WHERE %s = '%s';" %(reg_type,reg_info)
        fetch_data = mysql_conn.exec_readsql(sql)
        for item in fetch_data:
            # 将域名添加到列表中
            domains.append(item[0])
        return domains


    def get_reg_domain_from_reg(self,reg_type,reg_info):
        """
        功能：用注册信息反差时，直接获取关联域名与注册信息
        """
        global mysql_conn
        # 对注册信息进行转义处理
        reg_info = mysql_conn.escape_string(reg_info)
        conn_dm_reg = []
        sql = "SELECT domain,reg_name,reg_email,reg_phone FROM domain_reg_relationship WHERE %s = '%s';" %(reg_type,reg_info)
        fetch_data = mysql_conn.exec_readsql(sql)
        return fetch_data


    def escape_key(self,key):
        """
        功能：'.'不能出现在字典键值中，因此将ip，cname，邮箱等的'.'进行处理(后续改了思路，这个函数应该暂不会用到)
        """
        return key.replace('.','-')


    def escape_reg_info(reg_info):
        """
        功能：对注册信息进行转义处理
        """
        for reg_type in reg_info:
            if reg_info[reg_type] != '':
                reg_info[reg_type] = mysql_conn.escape_string(reg_info[reg_type])
        return reg_info


    def get_ip_conn_domains(self):
        """
        功能：获取由ip关联的域名

        * 以后考虑给domain_ip_relationship的标志为位怎么更新？？
        """
        global mysql_conn

        new_ip_conn_domains,new_ip_conn_reg = [],[]

        # 注意：只选择未更新过的关系进行添加
        sql = "SELECT IP FROM domain_ip_relationship WHERE domain = '%s' AND scan_flag = '%s';" %(self.source_domain,'NEW')
        fetch_data = mysql_conn.exec_readsql(sql)
        for item in fetch_data:
            ip = item[0]

            # 获取同ip的域名
            sql = "SELECT domain FROM domain_ip_relationship WHERE ip = '%s'; " %(ip)
            dm_fetch_data = mysql_conn.exec_readsql(sql)

            for record in dm_fetch_data:
                domain = record[0]
                if domain == self.source_domain:
                    # 与源域名相同则不进行处理
                    continue

                # 构建当前这个ip所关联到的域名集合 / 同一cname关联的同一域名不重复添加
                if {'conn':ip,'domain':domain} in new_ip_conn_domains:
                    continue

                new_ip_conn_domains.append({'conn':ip,'domain':domain})

                # 获取域名的注册信息
                reg_info = self.get_reg_info(domain)
                # 为了注册信息与域名一一对应，不进行去重
                new_ip_conn_reg.append({'conn':ip,'reg_info':reg_info})

            # 存储ip关联到的域名与注册信息
            # save_dns_conn_info(new_ip_conn_domains,new_ip_conn_reg,'ip')
        return new_ip_conn_domains,new_ip_conn_reg


    def get_cname_conn_domains(self):
        """
        功能：获取由cname关联的域名

        * 以后考虑给domain_cname_relationship的标志为位怎么更新？？
        """

        new_cname_conn_domains,new_cname_conn_reg = [],[]

        # 注意：只选择未更新过的关系进行添加
        sql = "SELECT cname FROM domain_cname_relationship WHERE domain = '%s' AND scan_flag = '%s';" %(self.source_domain,'NEW')
        # 103.242.101.249
        fetch_data = mysql_conn.exec_readsql(sql)
        for item in fetch_data:
            cname = item[0]

            # 获取同ip的域名
            sql = "SELECT domain FROM domain_cname_relationship WHERE cname = '%s'; " %(cname)
            dm_fetch_data = mysql_conn.exec_readsql(sql)

            for record in dm_fetch_data:
                domain = record[0]
                if domain == self.source_domain:
                    # 与源域名相同则不进行处理
                    continue

                # 同一cname关联的同一域名不重复添加
                if {'conn':cname,'domain':domain} in new_cname_conn_domains:
                    continue

                # 构建当前这个ip所关联到的域名集合
                new_cname_conn_domains.append({'conn':cname,'domain':domain})

                # 获取域名的注册信息
                reg_info = self.get_reg_info(domain)
                # 添加新域名的注册信息
                new_cname_conn_reg.append({'conn':cname,'reg_info':reg_info})

            # 存储cname关联到的域名和注册信息
            # self.save_dns_conn_info(new_cname_conn_domains,new_cname_conn_reg,'cname')
        return new_cname_conn_domains,new_cname_conn_reg


    def get_reg_info_domains(self):
        """
        功能：根据source_domain的注册信息获取相关信息

        email_domains:{
                      conn:---,
                      domains:[],
                      reg_info:[{},{}, ..., ]
                  }

        """
        reg_conn_domains = {
                            'reg_name':{'conn':'','domains':[],'reg_info':[]},\
                            'reg_email':{'conn':'','domains':[],'reg_info':[]},\
                            'reg_phone':{'conn':'','domains':[],'reg_info':[]}
                            }

        # 获取源域名的注册信息
        reg_info = self.get_reg_info(self.source_domain)

        for reg_type in reg_info:
            if reg_info[reg_type] == '':
                continue # 空的注册信息不进行关联

            # 获取当前注册信息关联到的域名和注册信息
            fetch_data = self.get_reg_domain_from_reg(reg_type,reg_info[reg_type])
            for domain,reg_name,reg_email,reg_phone in fetch_data:
                if domain == self.source_domain:
                    # 与源域名相同则不进行获取
                    continue
                # 关联因素
                reg_conn_domains[reg_type]['conn'] = reg_info[reg_type]
                # 将关联域名加入列表
                reg_conn_domains[reg_type]['domains'].append(domain)
                # 重复的注册信息也添加，目的在于与域名一一对应
                reg_info = {'reg_name':reg_name,'reg_email':reg_email,'reg_phone':reg_phone}
                reg_conn_domains[reg_type]['reg_info'].append(reg_info)

        # 存储注册信息关联所得的域名
        # self.save_reginfo_conn_info(reg_conn_domains)
        return reg_conn_domains


    def get_relative_domains(self):
        """
        功能：获取source的相关域名（外链和暗链域名）。且根据标志位每次获取上次未存储的，push到domain_conn_dm中
        """
        global monog_conn

        # source_domain新增的关联域名和注册信息列表
        new_relative_domains,new_relative_reginfo = [],[]

        fetch_data = mongo_conn.mongo_read('links_relation',{'domain':self.source_domain},{'domain':True,'relative_domains':True,'_id':False},limit_num = None)
        if fetch_data:
            item = fetch_data[0]
            domain = item['domain']
            # 令关联域名与标志位一一对应
            relative_domains_flag = zip(item['relative_domains']['relative_domains'],item['relative_domains']['flags'])
            for conn_domain,flag in relative_domains_flag:
                if not flag: # 说明是未存储过的外链关系
                    new_relative_domains.append(conn_domain) # 将域名加入关联列表
                    # 获取关联域名的注册信息
                    reg_info = self.get_reg_info(conn_domain)
                    new_relative_reginfo.append(reg_info)

            # 新建一个flag列表，用于将原flag全部置未True
            new_flag = [True] * len(item['relative_domains']['flags'])

        # print new_relative_domains
        # print new_relative_reginfo
        return new_relative_domains,new_relative_reginfo


    def save_reginfo_conn_info(self,reg_conn_domains):
        """
        功能：存储注册信息关联到的域名及注册信息
        param: reg_type: 注册信息的类型：reg_name/reg_email/reg_phone
        param: conn_info:某个类型注册信息关联到的域名与注册信息{'domains': [], 'reg_info': [], 'conn': '引起邮箱/电话/姓名'}

        param: reg_conn_domains = {
                            'reg_name':{'conn':'','domains':[],'reg_info':[]},\
                            'reg_email':{'conn':'','domains':[],'reg_info':[]},\
                            'reg_phone':{'conn':'','domains':[],'reg_info':[]}
                            }


        * 存储：关联元素set，关联域名与注册信息push，向列表中添加元素
        """

        global mongo_conn

        # 更新关联元素信息
        mongo_conn.mongo_update('domain_conn_dm_test',{'source_domain':self.source_domain},{'reg_name_domain.conn':reg_conn_domains['reg_name']['conn'],
                                                                                  'reg_email_domain.conn':reg_conn_domains['reg_email']['conn'],
                                                                                  'reg_phone_domain.conn':reg_conn_domains['reg_phone']['conn'],
                                                                                  },multi_flag=True)
        # 更新关联的域名和注册信息
        mongo_conn.mongo_push('domain_conn_dm_test',{'source_domain':self.source_domain},{'reg_name_domain.domains':{'$each':reg_conn_domains['reg_name']['domains']},
                                                                                 'reg_name_domain.reg_info':{'$each':reg_conn_domains['reg_name']['reg_info']},
                                                                                 'reg_email_domain.domains':{'$each':reg_conn_domains['reg_email']['domains']},
                                                                                 'reg_email_domain.reg_info':{'$each':reg_conn_domains['reg_email']['reg_info']},
                                                                                 'reg_phone_domain.domains':{'$each':reg_conn_domains['reg_phone']['domains']},
                                                                                 'reg_phone_domain.reg_info':{'$each':reg_conn_domains['reg_phone']['reg_info']},
                                                                                 })


    def save_dns_conn_info(new_conn_domains,new_conn_reg,conn_type):
        """
        功能：存储由域名ip和cname关联到的域名和注册信息
        param: new_conn_domains: 由ip或cname关联到的域名 [ {conn_ip:---,dm:--}, {conn_ip:---,dm:--}...] //{ip1:[dm1,dm2,...],ip2:[dm1,dm2,...],...}
        param: new_conn_reg: 由ip或cname关联到的注册信息 [{conn_ip:--,reg_info:{reg_name:--,reg_email:--,reg_phone:--},,{conn_ip:--,reg_info:{reg_name:--,reg_email:--,reg_phone:--}...]
        param: conn_type: 关联类型 字符串'cname'或'ip'
        """
        global mongo_conn
        domain_column = conn_type + '_domains' + '.domains'
        reg_column = conn_type + '_domains' + '.reg_info'

         # 更新关联的域名和注册信息
        mongo_conn.mongo_push('domain_conn_dm_test',{'source_domain':self.source_domain},
                                               {domain_column:{'$each':new_conn_domains},
                                               reg_column:{'$each':new_conn_reg}
                                               })


    def save_conn_info(self,reg_conn_domains,new_cname_conn_domains,new_cname_conn_reg,new_ip_conn_domains,new_ip_conn_reg,new_relative_domains,new_relative_reginfo):
        """
        功能：存储所有的关联域名与关联信息
        param: reg_conn_domains: 注册信息关联到的域名
               reg_conn_domains = {
                            'reg_name':{'conn':'','domains':[],'reg_info':[]},\
                            'reg_email':{'conn':'','domains':[],'reg_info':[]},\
                            'reg_phone':{'conn':'','domains':[],'reg_info':[]}
                            }
        param: new_cname_conn_domains :cname关联到的域名
        param: new_cname_conn_reg: cname关联到的注册信息
        param: new_ip_conn_domains :ip关联到的域名
        param: new_ip_conn_reg: ip关联到的注册信息

            new_××_conn_domains:[ {conn_××:---,dm:--}, {conn_××:---,dm:--}...]  //{ip1/cname1:[dm1,dm2,...],ip2/cname2:[dm1,dm2,...],...}这样不方便更新
            new_××_conn_reg: [{conn_ip:--,reg_info:{reg_name:--,reg_email:--,reg_phone:--},{conn_ip:--,reg_info:{reg_name:--,reg_email:--,reg_phone:--}...]
        """
        # # 更新关联元素信息
        # mongo_conn.mongo_update('domain_conn_dm_test',{'source_domain':self.source_domain},{'reg_name_domain.conn':reg_conn_domains['reg_name']['conn'],
        #                                                                           'reg_email_domain.conn':reg_conn_domains['reg_email']['conn'],
        #                                                                           'reg_phone_domain.conn':reg_conn_domains['reg_phone']['conn'],
        #                                                                           'visit_times':1
        #                                                                           },multi_flag=True)
        # # 更新关联的域名和注册信息
        # mongo_conn.mongo_push('domain_conn_dm_test',{'source_domain':self.source_domain},{'reg_name_domain.domains':{'$each':reg_conn_domains['reg_name']['domains']},
        #                                                                          'reg_name_domain.reg_info':{'$each':reg_conn_domains['reg_name']['reg_info']},
        #                                                                          'reg_email_domain.domains':{'$each':reg_conn_domains['reg_email']['domains']},
        #                                                                          'reg_email_domain.reg_info':{'$each':reg_conn_domains['reg_email']['reg_info']},
        #                                                                          'reg_phone_domain.domains':{'$each':reg_conn_domains['reg_phone']['domains']},
        #                                                                          'reg_phone_domain.reg_info':{'$each':reg_conn_domains['reg_phone']['reg_info']},
        #                                                                          'ip_domains.domains':{'$each':new_ip_conn_domains},
        #                                                                          'ip_domains.reg_info':{'$each':new_ip_conn_reg},
        #                                                                          'cname_domains.domains':{'$each':new_cname_conn_domains},
        #                                                                          'cname_domains.reg_info':{'$each':new_cname_conn_reg},
        #                                                                          'links_domains.domains':{'$each':new_relative_domains},
        #                                                                          'links_domains.reg_info':{'$each':new_relative_reginfo}
        #                                                                          })
        # 更新关联元素信息、关联域名和关联到的注册信息
        mongo_conn.mongo_any_update('domain_conn_dm_test',{'source_domain':self.source_domain},
                                                          {'$set':
                                                                  {'reg_name_domain.conn':reg_conn_domains['reg_name']['conn'],
                                                                   'reg_email_domain.conn':reg_conn_domains['reg_email']['conn'],
                                                                    'reg_phone_domain.conn':reg_conn_domains['reg_phone']['conn'],
                                                                    'visit_times':1
                                                                    },
                                                            '$push':
                                                                   {'reg_name_domain.domains':{'$each':reg_conn_domains['reg_name']['domains']},
                                                                    'reg_name_domain.reg_info':{'$each':reg_conn_domains['reg_name']['reg_info']},
                                                                    'reg_email_domain.domains':{'$each':reg_conn_domains['reg_email']['domains']},
                                                                    'reg_email_domain.reg_info':{'$each':reg_conn_domains['reg_email']['reg_info']},
                                                                    'reg_phone_domain.domains':{'$each':reg_conn_domains['reg_phone']['domains']},
                                                                    'reg_phone_domain.reg_info':{'$each':reg_conn_domains['reg_phone']['reg_info']},
                                                                    'ip_domains.domains':{'$each':new_ip_conn_domains},
                                                                    'ip_domains.reg_info':{'$each':new_ip_conn_reg},
                                                                    'cname_domains.domains':{'$each':new_cname_conn_domains},
                                                                    'cname_domains.reg_info':{'$each':new_cname_conn_reg},
                                                                    'links_domains.domains':{'$each':new_relative_domains},
                                                                    'links_domains.reg_info':{'$each':new_relative_reginfo}
                                                                    }
                                                            })


    def get_conn_domains(self):
        '''
        功能：构建source_domain与其关联域名关系表
        '''
        reg_conn_domains = self.get_reg_info_domains()
        new_cname_conn_domains,new_cname_conn_reg = self.get_cname_conn_domains()
        # print new_cname_conn_domains,new_cname_conn_reg
        new_ip_conn_domains,new_ip_conn_reg = self.get_ip_conn_domains()
        # print new_ip_conn_domains,new_ip_conn_reg
        new_relative_domains,new_relative_reginfo = self.get_relative_domains()
        # print new_relative_domains,new_relative_reginfo
        # 存储相关信息
        self.save_conn_info(reg_conn_domains,new_cname_conn_domains,new_cname_conn_reg,new_ip_conn_domains,new_ip_conn_reg,new_relative_domains,new_relative_reginfo)
        if new_ip_conn_domains != [] or new_relative_domains != []:
            print self.source_domain


def main():
    start = time.time()
    fetch_data = mongo_conn.mongo_read('domain_conn_dm_test',{'visit_times':0},{'source_domain':True,'_id':False},limit_num = None)

    for item in fetch_data:
        domain =  item['source_domain']
        # print domain
        conn_domains_getter = Domain_conn(domain)
        del conn_domains_getter
        print str(time.time() - start) + '\n'



if __name__ == '__main__':
    main()
