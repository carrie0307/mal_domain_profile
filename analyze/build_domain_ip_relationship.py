# encoding:utf-8
"""
    功能：根据mongo-domain_ip_cname更新分析层domain_ip_relationship表，ip_general_list表和domain_ip_relationship的数量统计信息

    author & date: csy 2018.01.17

    * 注意visit_times和slice
"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
import database.mysql_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.152','mal_domain_profile')
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')
import md5

"""MD5对象"""
m = md5.new()


def md5_id(string):
    global m
    m.update(string)
    md5_str = m.hexdigest()
    return md5_str

def get_ip_domain_relationship():
    """
    功能：根据mongo-domain_ip_cname每次新一轮获得的ip填充domain_ip_relationship表

    * 注意visit_times和slice   visit_times标志是用原始库中第几次的数据构建的关系
    """
    global mongo_conn
    global mysql_conn

    # slice=-1取最后一次的获取结果来更新域名与ip的关系
    fetch_data = mongo_conn.mongo_read('domain_ip_cname',{},{'domain':True,'maltype':True,'domain_ip_cnames':{'$slice':-1},'_id':False,'visit_times':True},limit_num=None)
    for item in fetch_data:
        # print item.keys()
        domain = item['domain']
        ips = item['domain_ip_cnames'][0]['ips']
        last_detect_time = item['domain_ip_cnames'][0]['insert_time']
        visit_times = item['visit_times']
        maltype = item['maltype']
        if ips:
            for ip in ips:
                ID =  md5_id(domain+ip)
                # print ID
                sql = "INSERT INTO domain_ip_relationship(ID,IP,domain,last_detect_time,maltype) VALUES('%s','%s','%s','%s','%s')\
                      ON DUPLICATE KEY UPDATE\
                      last_detect_time='%s'" %(ID,ip,domain,last_detect_time,maltype,last_detect_time)
                print sql
                mysql_conn.exec_cudsql(sql)
    # sql = "UPDATE domain_ip_relationship SET visit_times = %d;" %(visit_times)
    mysql_conn.exec_cudsql(sql)
    mysql_conn.commit()


def get_ip_info():
    """
    功能：根据mongo-domain_ip_cname最新一次的数据更新ip_general_list中的ip地理位置信息等

    * 注意visit_times和slice
    * 最新一次探测ip结果，获取最新的ip信息，更新ip总表

    """
    global mongo_conn
    global mysql_conn

    # slice=-1取最后一次的ip相关信息
    fetch_data = mongo_conn.mongo_read('domain_ip_cname',{},{'domain':True,'domain_ip_cnames':{'$slice':-1},'_id':False,'visit_times':True},limit_num=None)
    # print fetch_data
    for item in fetch_data:
        ips = item['domain_ip_cnames'][0]['ips']
        ip_geos = item['domain_ip_cnames'][0]['ip_geo']
        ip_state = item['domain_ip_cnames'][0]['ip_state']
        ip_as = item['domain_ip_cnames'][0]['ip_as']
        if ips:
            for index,ip in enumerate(ips):
                country = ip_geos[index]['country']
                region = ip_geos[index]['region']
                city = ip_geos[index]['city']
                oper = ip_geos[index]['oper']
                ASN = ip_as[index]['ASN']
                RIR = ip_as[index]['RIR']
                AS_CIDR = ip_as[index]['AS_cidr']
                AS_OWNER = ip_as[index]['AS_owner']
                state = ip_state[index]['state']
                state80 = ip_state[index]['state80']
                state443 = ip_state[index]['state443']
                visit_times = item['visit_times']

                # 这里用replace，从而使同一ip 的新信息可以覆盖旧的
                sql = "REPLACE INTO ip_general_list(ip,country,region,city,oper,ASN,RIR,AS_CIDR,AS_OWNER,state,state80,state443)\
                                              VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"\
                                              %(ip,country,region,city,oper,ASN,RIR,AS_CIDR,AS_OWNER,state,state80,state443)

                mysql_conn.exec_cudsql(sql)

    # 每次更新ip总表后将域名数量置为0
    # sql = "UPDATE ip_general_list SET visit_times = %s,dm_count=0;" %(visit_times)
    # mysql_conn.exec_cudsql(sql)
    mysql_conn.commit()


def count_ip_type_num():
    """
    根据domain_ip_relationship更新ip表中的gamble_num,porno_num等
    """
    global mongo_conn
    global mysql_conn

    sql = "SELECT maltype,ip,count(*) FROM domain_ip_relationship GROUP BY maltype,ip;"
    fetch_data = mysql_conn.exec_readsql(sql)
    for maltype,ip,type_num in fetch_data:
        print maltype,ip,type_num
        if maltype == '非法赌博':
            sql = "UPDATE ip_general_list SET gamble_num = %d WHERE ip = '%s';" %(type_num,ip)
        elif maltype == '色情':
            sql = "UPDATE ip_general_list SET porno_num = %d WHERE ip = '%s';" %(type_num,ip)
        mysql_conn.exec_cudsql(sql)
    #  通过sql语句统计dm_num即可
    # sql = "UPDATE ip_general_list SET dm_num = gamble_num + porno_num;"
    # mysql_conn.exec_cudsql(sql)
    mysql_conn.commit()



def main():
    get_ip_domain_relationship() # 更新域名-ip关系
    get_ip_info() # 更新ip总表相关信息
    count_ip_type_num() # 更新ip总表中的相关分类统计数量


if __name__ == '__main__':
    main()
