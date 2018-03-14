# encoding:utf-8
"""
    功能：对注册信息总表进行的分析

    实际运行时，加schedule模块，每天定时运行
"""
import schedule
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import MySQLdb
import database.mysql_operation


'''数据库连接'''
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')


def type_count(reg_type):
    """
    功能：统计每个注册信息(reg_name/reg_email/reg_phone/registrar)下对应不同类型的域名数量

    虽然遍历了2遍数据，但是减少了数据库操作
    """
    counter = 0
    whois_reg_type = 'domain_whois.' + reg_type
    sql = "select domain_index.maltype,%s,count(*) from domain_index,domain_whois\
           where domain_index.domain = domain_whois.domain \
           group by domain_index.maltype,%s;" %(whois_reg_type,whois_reg_type)

    reg_info_dict = {}

    # 对分类统计信息进行整合
    fetch_data = mysql_conn.exec_readsql(sql)
    for item in fetch_data:
        # reg_item是具体的reg_email/reg_name/reg_phone/registrar
        reg_item = item[1]
        count = int(item[2])

        if reg_item == '':
            continue

        if reg_item not in reg_info_dict:
            reg_info_dict[reg_item] = {'gamble':0,'porno':0}

        if str(item[0]) == '非法赌博':
            reg_info_dict[reg_item]['gamble'] = count
        if str(item[0]) == '色情':
            reg_info_dict[reg_item]['porno'] = count

    for item in reg_info_dict:

        gamble_count = reg_info_dict[item]['gamble']
        porno_count = reg_info_dict[item]['porno']
        domain_count = gamble_count + porno_count

        # 对注册信息进行转义
        reg_item = MySQLdb.escape_string(item)
        print reg_item,reg_type,domain_count,gamble_count,porno_count

        sql = "INSERT INTO reg_info_copy(item,reg_type,domain_count,gamble_count,porno_count)\
               VALUES('%s','%s',%d,%d,%d)\
               ON DUPLICATE KEY\
               UPDATE domain_count=%d,gamble_count=%d,porno_count=%d;"%(reg_item,reg_type,domain_count,gamble_count,porno_count,domain_count,gamble_count,porno_count)

        exec_res = mysql_conn.exec_cudsql(sql)
        if exec_res:
            counter += 1
            if counter == 100:
                mysql_conn.commit()
                counter = 0
    exec_res = mysql_conn.exec_cudsql(sql)
    mysql_conn.commit()

def main():
    for reg_type in ['reg_email','reg_name','reg_name','sponsoring_registrar']:
        type_count(reg_type)
        print reg_type + " 统计完成"

if __name__ == '__main__':
    main()
    mysql_conn.close_db()

    # schedule.every().day.at("10:30").do(job) # 每天十点三十分开始运行
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
