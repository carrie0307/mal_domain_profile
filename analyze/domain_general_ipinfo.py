# encoding:utf-8
"""
    功能：更新分析层domain_ip_relationship和ip_general_list更新domain_general_list中的ip信息
    author & date: csy 2018.01.17
    * 在运行build_domain_ip_rela后再运行此代码

"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
# import database.mongo_operation
import database.mysql_operation
# mongo_conn = database.mongo_operation.MongoConn('172.29.152.152','mal_domain_profile')
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')


def update_domain_ip():
    """
    功能：根据domain_ip_relationship更新域名总表domain_general_list中的的ip信息(IP地理位置和IP总数)
    """
    global mysql_conn

    sql = "SELECT ip,count(*),domain from domain_ip_relationship group by domain;"
    fetch_data = mysql_conn.exec_readsql(sql)
    for ip,ip_num,domain in fetch_data:
        print ip,int(ip_num),domain
        sql = "UPDATE domain_general_list SET IP = '%s',IP_num = %d WHERE domain = '%s';" %(ip,int(ip_num),domain)
        exec_res = mysql_conn.exec_cudsql(sql)
    mysql_conn.commit()
    mysql_conn.close_db()


def update_domain_ip_geo():
    """
    功能：根据新的ip_general_list中的地理位置信息，更新域名总表中的的ip的地理位置信息
    """
    global mysql_conn

    sql = "select distinct IP from domain_general_list WHERE IP != '';"
    fetch_data = mysql_conn.exec_readsql(sql)
    print fetch_data
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

def main():
    update_domain_ip() # 更新主表中ip信息
    update_domain_ip_geo() # 更新主表中ip地理位置信息



if __name__ == '__main__':
    # update_domain_ip_geo()
    sql = "SELECT country,region,city FROM ip_general_list WHERE ip = '0.0.0.0';"
    fetch_data_geo = mysql_conn.exec_readsql(sql)
    country,region,city = fetch_data_geo[0]
    print country,region,city
    geo = deal_geo_info(country,region,city)
    print geo
