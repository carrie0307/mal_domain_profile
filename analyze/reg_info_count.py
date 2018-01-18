# encoding:utf-8
"""
    对注册信息总表进行的分析
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import MySQLdb
import database.mysql_operation


'''数据库连接'''
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')


def ini_reg_info_table(reg_type):
    """
    通过whois表统计，向reg_info表插入初始的数据（item,type,count）
    # 无法跨表字段group by？
    """
    sql = "select %s,count(*) from domain_whois group by %s;" %(reg_type,reg_type)
    for item,domain_count in fetch_data:
        if item == '':
            # 空的注册信息不进行统计
            continue
        sql = "REPLACE INTO reg_info(item,reg_type,domain_count) VALUES('%s','%s',%d);" %(item,reg_type,domain_count)
        sql = MySQLdb.escape_string(sql)
        exec_res = mysql_conn.exec_cudsql(sql)
        # print item,domain_count
    print '初始化完成...'
    mysql_conn.commit()


def type_count(reg_type):
    """
    功能：统计每个注册信息下对应不同类型的域名数量
    """
    counter = 0
    whois_reg_type = 'domain_whois.' + reg_type
    sql = "select domain_index.maltype,%s,count(*) from domain_index,domain_whois\
           where domain_index.domain = domain_whois.domain \
           group by domain_index.maltype,%s;" %(whois_reg_type,whois_reg_type)
    fetch_data = mysql_conn.exec_readsql(sql)
    for item in fetch_data:
        print item
        if str(item[0]) == '非法赌博':
            sql = "UPDATE reg_info SET gamble_count = %d WHERE item = '%s';" %(int(item[2]),item[1])
        elif str(item[0]) == '色情':
            sql = "UPDATE reg_info SET porno_count = %d WHERE item = '%s';" %(int(item[2]),item[1])
        exec_res = mysql_conn.exec_cudsql(sql)
        if exec_res:
            counter += 1
            if counter == 100:
                mysql_conn.commit()
                counter = 0
    # 通过sql语句更新注册商对应的域名总量
    # sql = "UPDATE domain_registrar SET domain_count = gamble_count + porno_count;"
    # exec_res = mysql_conn.exec_cudsql(sql)
    mysql_conn.commit()

def main():
    for reg_type in ['reg_email','reg_name','reg_name']:
        ini_reg_info_table(reg_type)
        print reg_type + " 初始完成"
        type_count(reg_type)
        print reg_type + " 统计完成"



if __name__ == '__main__':
    main()
    mysql_conn.close_db()
