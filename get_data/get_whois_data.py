# encoding:utf-8
'''
    功能：前端whois展示数据获取(向get_whois_info函数传入要获取whois信息的域名即可)
'''
from __future__ import division
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import arrow
import datetime
import MySQLdb # 为转义而引入
from Base import Base

class Whois_info_getter(Base):

    def __init__(self,domain):
        self.domain = domain
        Base.__init__(self)

    def get_whois_info(self):
        '''
        功能：获取域名的whois相关信息
        param: domain: 要获取信息的域名
        return: res= {'talble_content':表格里显示的信息，'tag':标签中显示的信息(关联数量和生命周期)}
        '''

        # 获取基础whois信息
        whois_info = self.get_whois_key_info()
        if whois_info:
            reg_name,reg_email,reg_phone,sponsoring_registrar = whois_info['reg_name'],whois_info['reg_email'],whois_info['reg_phone'],whois_info['sponsoring_registrar']
            creation_date,expiration_date,update_date,insert_time = whois_info['creation_date'],whois_info['expiration_date'],whois_info['update_date'],whois_info['insert_time']
            insert_time = self.datetime2string(insert_time)
        else:
            return '无该域名whois信息'

        # 获取关联域名数量
        reg_name,reg_name_num,reg_email,reg_email_num,reg_phone,reg_phone_num = self.get_reg_dm_num(reg_name,reg_email,reg_phone)

        # 计算生命周期
        live_period = self.count_life_perios(creation_date,expiration_date)

        table_content = {}
        table_content = {'reg_name':whois_info['reg_name'],'reg_email':reg_email,'reg_phone':reg_phone,\
                         'sponsoring_registrar':sponsoring_registrar,'creation_date':creation_date,\
                         'expiration_date':expiration_date,'update_date':update_date,'insert_time':insert_time
                        }
        # 获取地理位置，验证电话，邮编
        self.get_whois_locate(table_content)

        # 整合结果
        res = {'table_content':table_content,
              'tag':{'reg_name_num':reg_name_num,'reg_email_num':reg_email_num,'reg_phone_num':reg_phone_num,'live_period':live_period}
              }
        return res


    def get_whois_key_info(self):
        '''
        功能：从domain_whois中获取所需数据
        param: domain: 要查询的域名
        return: [reg_name,reg_email,reg_phone,sponsoring_registrar,creation_date,expiration_date,update_date,insert_time] whis表中查到的信息
        return: [] 查不到该域名注册信息
        '''
        sql = "SELECT reg_name,reg_email,reg_phone,sponsoring_registrar,creation_date,expiration_date,update_date,insert_time\
               FROM domain_whois\
               WHERE domain = '%s';" %(self.domain)
        fetch_data = self.mysql_db.query(sql)
        if fetch_data:
            # print  fetch_data[0]
            return fetch_data[0]
        else:
            return []


    def datetime2string(self,date_time):
        '''
        将datetime转化为字符串
        '''
        if isinstance(date_time,datetime.datetime):
            date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
        return date_time


    def get_whois_locate(self,table_content):
        '''
        功能：获取whois信息中的地理位置和邮编信息
        param: domain: 要获取信息的域名
        return: geo:   whois中原始的地理位置信息
        return: postal_code:   whois中的邮编
        '''

        table_content['country_code'],table_content['city'],table_content['street'],table_content['province']= '','','',''
        table_content['reg_whois_country'],table_content['reg_whois_province'],table_content['reg_whois_city'],table_content['reg_whois_street'] = '','','',''
        table_content['postal_code'] = ''
        table_content['reg_phone_verify'] = ''


        sql = "SELECT reg_whois_country,reg_whois_province,reg_whois_city,reg_whois_street,\
                      reg_postal_country,reg_postal_province,reg_postal_city,reg_phone_country,reg_phone\
                      reg_phone_province,reg_phone_city,province,country_code,city,street,postal_code\
                FROM domain_locate WHERE domain = '%s';" %(self.domain)
        fetch_data = self.mysql_db.query(sql)

        if fetch_data:
            fetch_data = fetch_data[0]

            for key in ['reg_whois_country','reg_whois_province','reg_whois_city','reg_whois_street',\
                        'province','country_code','city','street','postal_code']:
                table_content[key] = fetch_data[key] if fetch_data[key] != 'None' else ''

            # print table_content
            # print table_content['reg_phone']
            # print table_content['postal_code']
            if table_content['reg_phone'] != '':
                if fetch_data['reg_phone_country'] == '外国':
                    table_content['reg_phone_verify'] = '合格'
                elif fetch_data['reg_phone_country'] != 'None' and fetch_data['reg_phone_province'] != 'None' and fetch_data['reg_phone_city'] != 'None':
                    table_content['reg_phone_verify'] = '合格'
                else:
                    table_content['reg_phone_verify'] = '不合格'
            else:
                table_content['reg_phone_verify'] = ''

            if table_content['postal_code'] and table_content['postal_code'] != 'None':
                if fetch_data['reg_postal_country'] == '外国':
                    table_content['reg_postal_verify'] = '合格'
                elif fetch_data['reg_postal_country'] != 'None' and fetch_data['reg_postal_province'] != 'None' and fetch_data['reg_postal_city'] != 'None':
                    table_content['reg_postal_verify'] = '合格'
                else:
                    table_content['reg_postal_verify'] = '不合格'
            else:
                print '---'
                table_content['reg_postal_verify'] = ''


    def get_reg_dm_num(self,reg_name,reg_email,reg_phone):
        '''
        功能： 获取注册信息关联的域名数量
        param: reg_name   注册姓名
        param: reg_email  注册邮箱
        param: reg_phone  注册电话
        注：1. 查不到该注册信息对应数量，则返回数量为'--'
           2.  注册信息如果为空，则返回'*'
        '''
        reg_name_num,reg_email_num,reg_phone_num = '*','*','*'

        if reg_name != '':
            reg_name = MySQLdb.escape_string(reg_name)
            sql = "SELECT domain_count FROM reg_info WHERE item = '%s';" %(reg_name)
            fetch_data = self.mysql_db.query(sql)
            reg_name_num = int(fetch_data[0]['domain_count']) if fetch_data else '--'
        if reg_email != '':
            reg_email = MySQLdb.escape_string(reg_email)
            sql = "SELECT domain_count FROM reg_info WHERE item = '%s';" %(reg_email)
            fetch_data = self.mysql_db.query(sql)
            reg_email_num = int(fetch_data[0]['domain_count']) if fetch_data else '--'
        if reg_phone != '':
            reg_phone = MySQLdb.escape_string(reg_phone)
            sql = "SELECT domain_count FROM reg_info WHERE item = '%s';" %(reg_phone)
            fetch_data = self.mysql_db.query(sql)
            reg_phone_num = int(fetch_data[0]['domain_count']) if fetch_data else '--'

        return reg_name,reg_name_num,reg_email,reg_email_num,reg_phone,reg_phone_num


    def count_life_perios(self,creation_date,expiration_date):
        '''
        功能：根据注册日期和过期日期计算生存时间
        return: return_live[*** 天(约**年)] 当日期为空时，返回 ‘--’

        提取主体部分处理
        0558520.com  2016-11-17 T19:31:05Z
        0471web.com  3/9/2017 7:06:03 AM
        0555.in      15-May-2014 06:31:06 UTC
        0-5baby.com  2018-01-06 00:00:00

        ' '无法提取出主体年月日，但arrow可处理其全部
        0-craft.com  2017-11-18T06:08:09.00Z

        '''
        # print creation_date,expiration_date
        if creation_date == '' or expiration_date == '':
            return '---'

        # 只对时间的主体部分处理
        creation_date = creation_date.split(' ')[0]
        start = arrow.get(creation_date)

        expiration_date = expiration_date.split(' ')[0]
        end = arrow.get(expiration_date)

        # 天数
        live_period = (end-start).days
        # 转化为年
        live_years = round(live_period / 365,2)

        return_live = str(live_period) + ' days(约' + str(live_years) + '年)'
        return return_live





if __name__ == '__main__':
    import torndb
    mysql_db = torndb.Connection(
        host = "172.26.253.3",
        database = "mal_domain_profile",
        user = "root",
        password = "platform",
        charset = "utf8",
    )

    # sql = "SELECT domain FROM domain_whois WHERE domain = '008858.com'"
    sql = "SELECT domain FROM domain_whois WHERE domain = '00000151.com'"
    fetch_data = mysql_db.query(sql)
    for domain in fetch_data:
        # try:
        domain = domain['domain']
        whois_info_getter = Whois_info_getter(domain)
        whois_info = whois_info_getter.get_whois_info()
        print whois_info['table_content']
        print whois_info['table_content']['reg_postal_verify']
        del whois_info_getter


    # whois_info_getter = Whois_info_getter('00887888.com')
    # print whois_info_getter.get_reg_dm_num('caojianlai','83869698@vip.qq.com','+86.2084491188')
    # print whois_info_getter.get_whois_key_info()
    # print whois_info_getter.get_whois_locate()
    # print whois_info_getter.count_life_perios('27-10-2014', '27-10-2018')
    # main()
    # get_whois_locate('00887888.com')
    # print count_life_perios('27-10-2014', '27-10-2018')
    # get_whois_key_info('0-360c.com')
    # reg_name,reg_name_num,reg_email,reg_email_num,reg_phone,reg_phone_num = get_reg_dm_num('caojianlai','83869698@vip.qq.com','+86.2084491188')
    # print reg_name,reg_name_num,reg_email,reg_email_num,reg_phone,reg_phone_num
