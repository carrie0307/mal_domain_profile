# encoding:utf-8
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
    sql = "select %s,count(*) from domain_whois group by %s;" %(whois_column,whois_column)
    fetch_data = mysql_conn.exec_readsql(sql)
    for item,domain_count in fetch_data:
        if item == '':
            continue
        print item,domain_count
        sql = "REPLACE INTO domain_registrar(domain_registrar_name,domains_count) VALUES('%s',%d);" %(item,domain_count)
        # sql = MySQLdb.escape_string(sql)
        exec_res = mysql_conn.exec_cudsql(sql)
        # print item,domain_count
    print '初始化完成...'
    mysql_conn.commit()


def type_count(whois_column):
    counter = 0
    whois_reg_type = 'domain_whois.' + whois_column
    sql = "select domain_index.maltype,%s,count(*) from domain_index,domain_whois\
           where domain_index.domain = domain_whois.domain \
           group by domain_index.maltype,%s;" %(whois_column,whois_column)
    fetch_data = mysql_conn.exec_readsql(sql)
    for item in fetch_data:
        print item
        if str(item[0]) == '非法赌博':
            sql = "UPDATE domain_registrar SET gamble_count = %d WHERE domain_registrar_name = '%s';" %(int(item[2]),item[1])
        else:
            sql = "UPDATE domain_registrar SET porno_count = %d WHERE domain_registrar_name = '%s';" %(int(item[2]),item[1])
        exec_res = mysql_conn.exec_cudsql(sql)
        if exec_res:
            counter += 1
            if counter == 100:
                mysql_conn.commit()
                counter = 0
    mysql_conn.commit()


if __name__ == '__main__':
    # ini_reg_info_table('sponsoring_registrar')
    type_count('sponsoring_registrar')
    # ini_reg_info_table('reg_email')
    # ini_reg_info_table('reg_name')
    # ini_reg_info_table('reg_phone')
    # ttt('reg_phone')
    # count_maltype('reg_email')
    # count_maltype('reg_name')
    # count_maltype('reg_phone')
    mysql_conn.close_db()
