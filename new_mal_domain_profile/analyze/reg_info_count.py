# encoding:utf-8
"""
    功能：对注册信息总表进行的分析

    实际运行时，加schedule模块，每天定时运行
"""
from configinfo import illegal_type_dict
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import MySQLdb
import database.mysql_operation


'''数据库连接'''
mysql_conn = database.mysql_operation.MysqlConn('10.245.146.38','root','platform','illegal_domains_profile','utf8')
'''分析层数据库连接'''
analysis_mysql_conn = database.mysql_operation.MysqlConn('10.245.146.38','root','platform','illegal_domains_profile_analysis','utf8')


def type_count(reg_type):
    """
    功能：统计每个注册信息(reg_name/reg_email/reg_phone/registrar)下对应不同类型的域名数量

    虽然遍历了2遍数据，但是减少了数据库操作
    """

    whois_reg_type = 'domain_whois.' + reg_type
    sql = "SELECT illegal_domains_index.illegal_type,%s,count(*) FROM illegal_domains_index,domain_whois\
           WHERE illegal_domains_index.domain = domain_whois.domain \
           GROUP BY illegal_domains_index.illegal_type,%s\
           ORDER BY %s;" %(whois_reg_type,whois_reg_type,whois_reg_type)
    # 对分类统计信息进行整合
    fetch_data = mysql_conn.exec_readsql(sql)

    counter = 0 # commit计数器
    domain_count = 0
    domain_count_info = ''
    last_reg_item = ''

    for item in fetch_data:
        # reg_item是具体的reg_email/reg_name/reg_phone/registrar
        illegal_type = str(item[0])
        reg_item = item[1]
        type_num = int(item[2]) # 该illegal_type对应的域名数量
        if not reg_item:
            continue

        if last_reg_item and last_reg_item != reg_item:
            # 一个新的注册信息
            print last_reg_item,domain_count,domain_count_info
            last_reg_item = MySQLdb.escape_string(last_reg_item)
            sql = "INSERT INTO reg_info(item,reg_type,domain_count,domain_count_info)\
                   VALUES('%s','%s',%d,'%s')ON DUPLICATE KEY\
                   UPDATE domain_count=%d,domain_count_info='%s';"%(last_reg_item,reg_type,domain_count,domain_count_info,domain_count,domain_count_info)
            exec_res = analysis_mysql_conn.exec_cudsql(sql)
            if exec_res:
                counter += 1
                if counter == 100:
                    analysis_mysql_conn.commit()
                    counter = 0
            domain_count = 0
            domain_count_info = ''

        domain_count_info = domain_count_info + str(illegal_type_dict[str(illegal_type)]) + ':' + str(type_num) + ';'
        domain_count += type_num
        last_reg_item = reg_item

    analysis_mysql_conn.commit()


def main():
    for reg_type in ['reg_email','reg_name','reg_phone','sponsoring_registrar']:
        type_count(reg_type)
        print reg_type + " 统计完成"

if __name__ == '__main__':
    main()
    mysql_conn.close_db()
    analysis_mysql_conn.close_db()

    # schedule.every().day.at("10:30").do(job) # 每天十点三十分开始运行
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
