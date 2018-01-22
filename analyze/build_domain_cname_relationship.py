# encoding:utf-8
"""
    功能：根据mongo-domain_ip_cname更新分析层domain_cname_relationship表(用于关联关系的构建)

    author & date: csy 2018.01.17
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

def get_cname_domain_relationship():
    """
    功能：根据mongo-domain_ip_cname每次新一轮获得的cname填充domain_ip_relationship表

    * 注意visit_times和slice  visit_times标志是用原始库中第几次的数据构建的关系
    """
    global mongo_conn
    global mysql_conn

    # slice=-1取最后一次的获取结果来更新域名与ip的关系
    fetch_data = mongo_conn.mongo_read('domain_ip_cname',{},{'domain':True,'domain_ip_cnames':{'$slice':1},'_id':False,'visit_times':True},limit_num=None)
    for item in fetch_data:
        # print item.keys()
        domain = item['domain']
        cnames = item['domain_ip_cnames'][0]['cnames']
        last_detect_time = item['domain_ip_cnames'][0]['insert_time']
        visit_times = item['visit_times']
        if cnames:
            for cname in cnames:
                ID =  md5_id(domain+cname)
                # print ID
                sql = "INSERT INTO domain_cname_relationship(ID,cname,domain,last_detect_time) VALUES('%s','%s','%s','%s')\
                      ON DUPLICATE KEY UPDATE\
                      last_detect_time='%s'" %(ID,cname,domain,last_detect_time,last_detect_time)
                # print sql
                mysql_conn.exec_cudsql(sql)
    # sql = "UPDATE domain_cname_relationship SET visit_times = %d;" %(visit_times)
    # mysql_conn.exec_cudsql(sql)
    mysql_conn.commit()



def main():
    get_cname_domain_relationship() # 更新域名-ip关系



if __name__ == '__main__':
    main()
