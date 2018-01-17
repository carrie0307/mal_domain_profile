# encoding:utf-8
"""
    对注册商总表进行统计
"""
import sys
import MySQLdb
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mysql_operation


'''数据库连接'''
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')


def ini_reg_info_table(whois_column):
    """
    通过whois表统计，向reg_info表插入初始的数据（item,type,count）
    """
    global mysql_conn
    sql = "select %s,count(*) from domain_whois group by %s;" %(whois_column,whois_column)
    fetch_data = mysql_conn.exec_readsql(sql)
    for item,domain_count in fetch_data:
        if item == '':
            continue
        print item,domain_count
        # sql = "REPLACE INTO domain_registrar(domain_registrar_name,domains_count) VALUES('%s',%d);" %(item,domain_count)
        sql = "INSERT INTO domain_registrar(domain_registrar_name,domains_count) VALUES('%s',%d)\
              ON DUPLICATE KEY UPDATE domains_count=%d" %(item,domain_count,domain_count)
        sql = MySQLdb.escape_string(sql) # 转义chuli
        exec_res = mysql_conn.exec_cudsql(sql)
        print item,domain_count
    print '初始化完成...'
    mysql_conn.commit()


def type_count(whois_column):
    """
    功能：统计每个注册商下各类型域名的数量
    """
    global mysql_conn
    counter = 0 # commit计数器
    whois_reg_type = 'domain_whois.' + whois_column
    sql = "select domain_index.maltype,%s,count(*) from domain_index,domain_whois\
           where domain_index.domain = domain_whois.domain \
           group by domain_index.maltype,%s;" %(whois_column,whois_column)
    fetch_data = mysql_conn.exec_readsql(sql)
    for item in fetch_data:
        print item
        if str(item[0]) == '非法赌博':
            sql = "UPDATE domain_registrar SET gamble_count = %d WHERE domain_registrar_name = '%s';" %(int(item[2]),item[1])
        elif str(item[0]) == '色情':
            sql = "UPDATE domain_registrar SET porno_count = %d WHERE domain_registrar_name = '%s';" %(int(item[2]),item[1])
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


if __name__ == '__main__':
    ini_reg_info_table('sponsoring_registrar')
    type_count('sponsoring_registrar')
    mysql_conn.close_db()
