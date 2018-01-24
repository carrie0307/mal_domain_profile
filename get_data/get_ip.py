# encoding:utf-8
'''
    功能：通过get_ip_info函数获取ip分析相关信息
    注：ip变化频率暂时置为了空
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from Base import Base


class IP_data_getter(Base):

    def __init__(self,domain):
        self.domain = domain
        Base.__init__(self)

    def deal_geo_info(self,country,region,city):
        """
        组装完整的地理位置信息
        """
        geo = country
        if country == '香港' or country == '台湾' or country == '内网IP':
            return geo
        elif region != '0':
            geo = geo + '-' + region
        if city != '0' and city != region:
            geo = geo + '-' + city
        return geo


    def deal_state_info(self,state):
        """
        功能：对80端口状态信息进行处理
        """
        if state == 'open':
            return '80端口-开放'
        elif state == 'closed':
            return '80端口-关闭'
        else:
            # 对应filter和没有scan字段的情况(0)
            return '无法探测到'


    def get_table_ip_info(self):
        '''
        功能： 获取表格中所需要的ip信息
        '''
        sql = "SELECT a.IP,a.last_detect_time,b.state80,b.country,b.region,b.city,b.oper,b.ASN,b.AS_OWNER\
        FROM (SELECT domain_ip_relationship.IP,domain_ip_relationship.last_detect_time\
        FROM domain_ip_relationship WHERE domain = '%s') AS a\
        LEFT JOIN ip_general_list as b ON a.IP = b.IP;" %(self.domain)

        fetch_data = self.mysql_db.query(sql)
        table_ip_info = []

        if fetch_data:
            for item in fetch_data:

                ip,last_detect_time,state,country,region,city,oper,asn,as_owner = item

                item['geo'] = self.deal_geo_info(item['country'],item['region'],item['city'])
                del item['country']
                del item['region']
                del item['city']

                item['state80'] = self.deal_state_info(item['state80'])
                table_ip_info.append(item)
        return table_ip_info


    def get_domain_ip_num(self):
        '''
        功能： 获取曾给该域名提供服务的不重复的ip数量(the num of dinstinct IPs that hosted the domain ever)
        '''
        sql = "SELECT IP_num FROM domain_general_list WHERE domain = '%s';" %(self.domain)
        fetch_data = self.mysql_db.query(sql)
        if fetch_data:
            ip_num = int(fetch_data[0]['IP_num'])
            return ip_num
        else:
            print '无此域名记录'
            return


    def get_ip_change_frequency(self):
        '''
        功能： 获取ip变化频率数值
        '''
        return '---'


    def get_ip_info(self):
        '''
        功能：获取ip分析部分所需数据
        return ip_info: {ip_num:ip数量,ip_change_frequency:ip变化频率，table_info:[{},{}] # 表格中所需数据，每个元素为一个字典，该字典对应表中的一行}
        eg. {'ip_num': 2, 'table_info': [{'state80': '80端口开放', 'IP': u'52.73.207.56', 'last_detect_time': u'2018-01-09 20:43:25', 'AS_OWNER': u'AMAZON-AES - Amazon.com', 'ASN': u'14618', 'geo': u'中国山东', 'oper': u'电信'}}], 'ip_change_frequency': '---'}
        '''
        ip_info = {'ip_num':None,'ip_change_frequency':None, 'table_info':[],}
        ip_num = self.get_domain_ip_num()
        print ip_num
        ip_info['ip_num'] = ip_num
        if ip_info['ip_num'] == 0:
            return '该域名无ip'
        elif ip_info['ip_num'] == None:
            return None
        else:# 正常存在到ip的情况
            ip_info['table_info'] = self.get_table_ip_info()
            ip_info['ip_change_frequency'] = self.get_ip_change_frequency()

        return ip_info


if __name__ == '__main__':

    ip_data_getter = IP_data_getter('0-dian.com')
    print ip_data_getter.get_ip_info()
