# coding=utf-8
import urllib2
import Queue
import threading
import sys
sys.path.append("..") # 回退到上一级目录
import database.mysql_operation

'''数据库连接'''
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')

domain_q = Queue.Queue()
res_q = Queue.Queue()

'''线程数量'''
thread_num = 15

def get_domains():
    '''
    功能：从数据库读取未获取页面icp信息的域名
    '''
    global mysql_conn
    sql = "SELECT domain FROM domain_general_list WHERE http_code = 'None';"
    fetch_data = mysql_conn.exec_readsql(sql)
    if fetch_data == False:
        print "获取数据有误..."
        return False
    for domain in fetch_data:
        domain_q.put(domain[0])


def get_http_code():
    global domain_q
    global res_q

    while not domain_q.empty():
        domain = domain_q.get()
        url = 'http://www.' + domain
        try:
            resp = urllib2.urlopen(url,timeout=10)
            code = resp.code
        except urllib2.HTTPError, e:
            code = e.code
        except Exception, e:
            code = 'ERROR'
        res_q.put([domain,code])
    print 'httpcode获取完成...'


def save_res():
    global res_q
    global mysql_conn
    counter = 0

    while True:
        try:
            domain,code = res_q.get(timeout=150)
        except Queue.Empty:
            print 'save over ... \n'
            break
        print counter, domain, code
        sql = "UPDATE domain_general_list SET http_code = '%s' WHERE domain = '%s';" %(code,domain)
        exec_res = mysql_conn.exec_cudsql(sql)
        if exec_res:
            counter += 1
            # print "counter : " + str(counter)
            if counter == 500:
                mysql_conn.commit()
                counter = 0
    mysql_conn.commit()
    print "存储完成... "
    mysql_conn.close_db()


if __name__ == '__main__':
    get_domains()
    get_httpcode_td = []
    for _ in range(thread_num):
        get_httpcode_td.append(threading.Thread(target=get_http_code))
    for td in get_httpcode_td:
        td.start()
    print 'save res ...\n'
    save_db_td = threading.Thread(target=save_res)
    save_db_td.start()
    save_db_td.join()
