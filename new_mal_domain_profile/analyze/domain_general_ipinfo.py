# encoding:utf-8
"""
    功能：根据分析层domain_ip_relationship和ip_general_list更新domain_general_list中的ip信息


"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mysql_operation
mysql_conn = database.mysql_operation.MysqlConn('10.245.146.38','root','platform','illegal_domains_profile_analysis','utf8')
mysql_conn_raw = database.mysql_operation.MysqlConn('10.245.146.38','root','platform','illegal_domains_profile','utf8')


def update_domain_ip():
    """
    功能：根据domain_ip_relationship更新域名总表domain_general_list中的的ip信息(IP地理位置和IP总数)
    """
    global mysql_conn

    # domain_Ip_relationship包含有历史记录，因此这里的count是历史以来该域名所有的ip数量
    sql = "SELECT domain,any_value(ip),count(*) from domain_ip_relationship group by domain;"
    fetch_data = mysql_conn.exec_readsql(sql)
    for domain,ip,ip_num in fetch_data:
        print ip,int(ip_num),domain,illegal_type
        sql = "UPDATE domain_general_list SET IP = '%s',IP_num = %d WHERE domain = '%s';" %(ip,int(ip_num),domain)
        exec_res = mysql_conn.exec_cudsql(sql)
    mysql_conn.commit()


def update_domain_ip_geo():
    """
    功能：根据新的ip_general_list中的地理位置信息，更新域名总表中的的ip的地理位置信息
    """
    global mysql_conn

    sql = "select distinct IP from domain_general_list WHERE IP != '';"
    fetch_data = mysql_conn.exec_readsql(sql)
    for ip in fetch_data:
        ip = ip[0]
        # sprint ip
        sql = "SELECT country,region,city FROM ip_general_list WHERE ip = '%s'" %(ip)
        fetch_data_geo = mysql_conn.exec_readsql(sql)
        country,region,city = fetch_data_geo[0]
        geo = deal_geo_info(country,region,city)
        print geo
        sql = "UPDATE domain_general_list SET IP_geo = '%s' WHERE IP = '%s';" %(geo,ip)
        exec_res = mysql_conn.exec_cudsql(sql)
        mysql_conn.commit()



def deal_geo_info(country,region,city):
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

def temp():
    sql = "SELECT domain,illegal_type FROM illegal_domains_index;"
    fetch_data = mysql_conn_raw.exec_readsql(sql)
    mysql_conn_raw.close_db()
    for domain, illegal_type in fetch_data:
        print domain,illegal_type
        sql = "UPDATE domain_general_list SET dm_type = '%s' WHERE domain = '%s';" %(illegal_type,domain)
        mysql_conn.exec_cudsql(sql)
    mysql_conn.commit()


def main():
    temp()
    # update_domain_ip() # 更新主表中ip信息
    # update_domain_ip_geo() # 更新主表中ip地理位置信息
    mysql_conn.close_db()



if __name__ == '__main__':
    main()

    # update_domain_ip_geo()
    # sql = "SELECT country,region,city FROM ip_general_list WHERE ip = '0.0.0.0';"
    # fetch_data_geo = mysql_conn.exec_readsql(sql)
    # country,region,city = fetch_data_geo[0]
    # print country,region,city
    # geo = deal_geo_info(country,region,city)
    # print geo
