# encoding:utf-8
"""
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
    根据每次新一轮获得的ip填充domain_ip_relationship表
    (先据第一次的跑了，以后每次跑slice-1的情况)
    * 下次跑注意visit_times和slice
    """
    fetch_data = mongo_conn.mongo_read('domain_ip_cname',{},{'domain':True,'maltype':True,'domain_ip_cnames':{'$slice':1},'_id':False,'visit_times':True},limit_num=None)
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
    先根据第一次ip的数据跑完了
    * 下次跑注意visit_times和slice
    从最新一次探测ip结果，获取最新的ip信息，更新ip总表

    """
    fetch_data = mongo_conn.mongo_read('domain_ip_cname',{},{'domain':True,'domain_ip_cnames':{'$slice':1},'_id':False,'visit_times':True},limit_num=None)
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
    sql = "SELECT maltype,ip,count(*) FROM domain_ip_relationship GROUP BY maltype,ip;"
    fetch_data = mysql_conn.exec_readsql(sql)
    for maltype,ip,type_num in fetch_data:
        print maltype,ip,type_num
        if maltype == '非法赌博':
            sql = "UPDATE ip_general_list SET gamble_num = %d WHERE ip = '%s';" %(type_num,ip)
        elif maltype == '色情':
            sql = "UPDATE ip_general_list SET porno_num = %d WHERE ip = '%s';" %(type_num,ip)
        mysql_conn.exec_cudsql(sql)
    #  然后通过sql语句统计dm_num即可
    mysql_conn.commit()









if __name__ == '__main__':
    # get_ip_domain_relationship()
    # get_ip_info()
    count_ip_type_num()
