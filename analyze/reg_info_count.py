# encoding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mysql_operation


'''数据库连接'''
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')


def ini_reg_info_table(reg_type):
    """
    通过whois表统计，向reg_info表插入初始的数据（item,type,count）
    # 无法跨表字段group by？
    """
    sql = "select %s,count(*) from domain_whois group by %s;" %(reg_type,reg_type)
    print '--'
    for item,domain_count in fetch_data:
        if item == '':
            item = 'null_' + reg_type # 由于表中有主键，因此这样处理空值
        sql = "REPLACE INTO reg_info(item,reg_type,domain_count) VALUES('%s','%s',%d);" %(item,reg_type,domain_count)
        sql = MySQLdb.escape_string(sql)
        exec_res = mysql_conn.exec_cudsql(sql)
        # print item,domain_count
    print '初始化完成...'
    mysql_conn.commit()



def count_maltype(reg_type):
    """
    根据domain_Index中的maltype字段，更新各类型域名数量
    """
    counter = 0

    sql = "SELECT item FROM reg_info WHERE reg_type = '%s' AND gamble_count = -1;" %(reg_type)
    whois_reg_type = 'domain_whois.' + reg_type
    fetch_data = mysql_conn.exec_readsql(sql)
    for item in fetch_data:
        if 'null' in item[0]:
            item[0] == ''
        sql = "SELECT domain_index.maltype,count(*) FROM domain_index,domain_whois\
               WHERE domain_index.domain = domain_whois.domain and %s = '%s' \
               group by domain_index.maltype;" %(whois_reg_type,item[0])
        fetch_data = mysql_conn.exec_readsql(sql)
        num_dict = {'非法赌博':0,'色情':0}
        for record in fetch_data:
            num_dict[str(record[0])] = int(record[1])
        # print num_dict
        sql = "UPDATE reg_info SET gamble_count = %d,porno_count = %d WHERE item = '%s';" %(num_dict['非法赌博'],num_dict['色情'],item[0])
        sql = escape_string(sql)
        exec_res = mysql_conn.exec_cudsql(sql)
        if exec_res:
            counter += 1
            if counter == 500:
                counter = 0
                mysql_conn.commit()
    mysql_conn.commit()
        # print fetch_data


def type_count(reg_type):
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
        else:
            sql = "UPDATE reg_info SET porno_count = %d WHERE item = '%s';" %(int(item[2]),item[1])
        exec_res = mysql_conn.exec_cudsql(sql)
        if exec_res:
            counter += 1
            if counter == 100:
                mysql_conn.commit()
                counter = 0
    mysql_conn.commit()


if __name__ == '__main__':
    # ini_reg_info_table('reg_email')
    # ini_reg_info_table('reg_name')
    # ini_reg_info_table('reg_phone')
    ttt('reg_phone')
    # count_maltype('reg_email')
    # count_maltype('reg_name')
    # count_maltype('reg_phone')
    mysql_conn.close_db()
