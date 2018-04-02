# encoding:utf-8
"""
    功能：根据mongo-domain_ip_cname更新分析层domain_ip_relationship表，ip_general_list表和domain_ip_relationship的数量统计信息
    0. 更新的表：domain_ip_relationship,domain_cname_relationship,ip_general_list
    1. 每次完整跑完一次ip_history后运行build_ip_domain_relationship,运行完后domain_ip_relationship，domain_ip_relationship，ip_general_list中的visit_time与mongo相同
    2. 每次运行此代码时，如果某domain_ip对已经存在，则更新detect time;反之则直接插入记录

    注：1） 每次构建ip - domain 对时，如果某 domain - ip 对已经存在，则只更新探测时间;如果不存在，则直接插入;因此, domain - ip 表内的是domain曾有
    过ip的并集;
        2) cname - domain 表同上

    现在先以visit_times=5的情况重新建立了以上3个表

"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
import database.mysql_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.151','new_mal_domain_profile')
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')
import md5

"""MD5对象"""
m = md5.new()


def md5_id(string):
    global m
    m.update(string)
    md5_str = m.hexdigest()
    return md5_str


def get_ip_cname_domain_relationship():
    """
    功能：根据mongo-domain_ip_cname每次新一轮获得的ip填充domain_ip_relationship表和domain_cname_relationship表

    domain_ip_relationship:为ip反查域名服务
    domain_cname_relationship: 为cname反查域名服务
    ip_general_list: ip总表

    * 注意visit_times和slice   visit_times标志是用原始库中第几次的数据构建的关系
    """
    global mongo_conn
    global mysql_conn

    # slice=-1取最后一次的获取结果来更新域名与ip的关系
    fetch_data = mongo_conn.mongo_read('domain_ip_cname',{},{'domain':True,'maltype':True,'domain_ip_cnames':{'$slice':-1},'_id':False,'visit_times':True},limit_num=None)
    for item in fetch_data:
        domain = item['domain']
        maltype = item['maltype']
        ips = item['domain_ip_cnames'][0]['ips']
        ip_geos = item['domain_ip_cnames'][0]['ip_geo']
        ip_as = item['domain_ip_cnames'][0]['ip_as']
        ip_state = item['domain_ip_cnames'][0]['ip_state']
        cnames = item['domain_ip_cnames'][0]['cnames']
        detect_time = item['domain_ip_cnames'][0]['insert_time']

        visit_times = item['visit_times']

        # 建立ip-domiain关系
        build_ip_domain_relationship(domain,maltype,ips,detect_time,ip_geos,visit_times)
        # 建立cname-domiain关系
        build_cname_domain_relationship(domain,maltype,cnames,detect_time,visit_times)
        # 构建ip_gemeral_list （ip总表）
        build_ip_general_list(ips,ip_geos,ip_state,ip_as,visit_times)

    # 更新ip表中的gamble_num,porno_num等
    update_ip_general_list_count()


def build_ip_domain_relationship(domain,maltype,ips,detect_time,ip_geos,visit_times):
    '''
    功能：对当前数据信息建立domain-ip对，并组装sql语句
    param:domain
    param:maltype
    param:ips
    param:detect_time
    '''
    if ips:
        for index,ip in enumerate(ips):
            country = ip_geos[index]['country']
            region = ip_geos[index]['region']
            # 创建ID
            ID =  md5_id(domain+ip)
            # 整理地理位置信息
            if country == '香港' or country == '台湾' or country == '澳门':
                # 港澳台国家写为“中国”，省份写为”香港“，”澳门“和”台湾“
                region = country
                country =  '中国'
            elif country == '中国' and (region[-1] == '市' or region[-1] == '省'):
                # 不要‘省’和‘市’字
                region = region[:len(region)-1]

            sql = "INSERT INTO domain_ip_relationship(ID,IP,domain,last_detect_time,maltype,ip_country,ip_province,visit_times)\
                 VALUES('%s','%s','%s','%s','%s','%s','%s','%d')\
                  ON DUPLICATE KEY\
                  UPDATE last_detect_time='%s',visit_times='%d'" %(ID,ip,domain,detect_time,maltype,country,region,visit_times,detect_time,visit_times)
            mysql_conn.exec_cudsql(sql)
        # 执行完所有commit一次
        mysql_conn.commit()


def build_cname_domain_relationship(domain,maltype,cnames,detect_time,visit_times):
    '''
    功能：对mongo数据信息建立domain-cname对，并组装sql语句
    param:domain
    param:maltype
    param:cnames
    param:detect_time
    '''
    if cnames:
        for cname in cnames:
            ID = md5_id(domain+cname)
            sql = "INSERT INTO domain_cname_relationship(ID,cname,domain,last_detect_time,visit_times)\
                   VALUES('%s','%s','%s','%s','%d')\
                  ON DUPLICATE KEY\
                  UPDATE last_detect_time='%s',visit_times='%d';" %(ID,cname,domain,detect_time,visit_times,detect_time,visit_times)
            mysql_conn.exec_cudsql(sql)
        # 执行完所有commit一次
        mysql_conn.commit()


def build_ip_general_list(ips,ip_geos,ip_state,ip_as,visit_times):
    '''
    功能：构建ip_gemeral_list （ip总表）
    param:
    '''

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

            # 这里用replace，从而使同一ip 的新信息可以覆盖旧的
            sql = "REPLACE INTO ip_general_list(ip,country,region,city,oper,ASN,RIR,AS_CIDR,AS_OWNER,state,state80,state443,visit_times)\
                   VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%d');"\
                 %(ip,country,region,city,oper,ASN,RIR,AS_CIDR,AS_OWNER,state,state80,state443,visit_times)
            # 执行
            mysql_conn.exec_cudsql(sql)
        # 提交
        mysql_conn.commit()

def update_ip_general_list_count():
    """
    功能：根据domain_ip_relationship更新ip表中的gamble_num,porno_num等
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
    # 通过sql语句统计dm_num即可
    sql = "UPDATE ip_general_list SET dm_num = gamble_num + porno_num;"
    mysql_conn.exec_cudsql(sql)
    mysql_conn.commit()


def main():
    get_ip_cname_domain_relationship()

if __name__ == '__main__':
    main()
