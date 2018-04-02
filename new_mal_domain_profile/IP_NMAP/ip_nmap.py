#-*- coding:utf-8 -*-
"""
    扫描NMAP默认IP端口代码
"""
import nmap # 导入 nmap.py 模块
import datetime
import threading
import time
import Queue

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
import database.mysql_operation
mongo_conn = database.mongo_operation.MongoConn('10.245.146.38','illegal_domains_profile')
mysql_conn = database.mysql_operation.MysqlConn('10.245.146.38','root','platform','illegal_domains_profile_analysis','utf8')
collection_name = 'ip_port_detail'

ip_q = Queue.Queue()
mysql_res_q = Queue.Queue()
mongo_res_q = Queue.Queue()
thread_num = 2

def get_ips():
    '''
    功能：从ip主表读取IP
    '''
    global ip_q

    sql = "SELECT IP FROM ip_general_list LIMIT 10;"
    fetch_data = mysql_conn.exec_readsql(sql)
    for item in fetch_data:
        ip = item[0]
        ip_q.put(ip)


def get_ip_state():
    '''
    功能：通过NMAP获取IP状态
    '''
    global mysql_res_q
    global mongo_res_q
    global ip_q

    while ip_q:
        ip = ip_q.get()
        ip_info = {}
        exception_message = ''
        state,state80,state443 = '--','--','--'

        try:
            nm = nmap.PortScanner()
        except nmap.PortScannerError:
            exception_message = 'NMap Not Found'
            # 加入队列重新获取
            ip_q.put(ip)
            # ip_info['exception_message'] = exception_message
            # ip_info['insert_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # mysql_res_q.put([ip,state,state80,state443])
            # mongo_res_q.put([ip, ip_info])

        try:
            res = nm.scan(hosts=ip,arguments='-F -A -Pn ')
        except Exception,e:
            exception_message = 'Scan Error: ' + str(e)
            # 加入队列重新获取
            ip_q.put(ip)
            # ip_info['exception_message'] = exception_message
            # ip_info['insert_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # mysql_res_q.put([ip,state,state80,state443])
            # mongo_res_q.put([ip, ip_info])

        if res['scan'] and 'status' in res['scan'][ip]:
            # 获取主机状态信息
            ip_info['status'] = res['scan'][ip]['status']
            state = res['scan'][ip]['status']['state']

        if res['scan'] and 'tcp' in res['scan'][ip]:
            # 获取各个端口信息
            for port in res['scan'][ip]['tcp']:
                ip_info['port' + str(port)] = res['scan'][ip]['tcp'][port]
                if port == 80:
                    state80 = res['scan'][ip]['tcp'][port]['state']
                elif port == 443:
                    state443 = res['scan'][ip]['tcp'][port]['state']
        ip_info['exception_message'] = exception_message
        ip_info['insert_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 加入结果存储队列
        mysql_res_q.put([ip,state,state80,state443])
        mongo_res_q.put([ip, ip_info])


def mysql_save_res():
    '''
    功能：更新mysql-IP主表中的端口信息
    '''
    global mysql_res_q
    counter = 0

    while True:
        try:
            ip,state,state80,state443 = mysql_res_q.get(timeout = 200)
        except Queue.Empty:
            print 'mysql存储获取完成 ... '
            break

        sql = "UPDATE ip_general_list SET state = '%s', state80 = '%s', state443 = '%s'\
               WHERE ip = '%s';" %(state, state80, state443,ip)
        exec_res = mysql_conn.exec_cudsql(sql)
        print ip + ' mysql saved ...'
        if exec_res:
            counter += 1
            print "counter:" + str(counter)
            if counter == 100:
                mysql_conn.commit()
                counter = 0
        else:
            # 存储出现异常则加入重新存储
            mysql_res_q.put([ip,state,state80,state443])
    mysql_conn.commit()
    print 'mysql存储完成...'


def mongo_save_res():
    '''
    功能：在mongo中存储IP端口信息
    '''
    global mongo_res_q
    global collection_name
    print 'mongo save start ...'

    while True:
        try:
            ip, ip_info = mongo_res_q.get(timeout=200)
        except Queue.Empty:
            print 'mongo存储获取完成 ... '
            break
        # mongo存储
        try:
            # 因为mongo_conn没有封装异常处理，因此在这里添加try except
            mongo_conn.mongo_any_update_new(collection_name,{'ip':ip},
                                                                {
                                                                '$set':{'ip':ip,},
                                                                '$inc':{'visit_times':1},
                                                                '$push':{'ip_state_records':ip_info}
                                                                },
                                                                True
                                        )
            print ip + ' mongo saved ...'
        except Exception,e:
            print ip + '   ' + str(e)
            # 存储出现异常则加入队列重新存储
            mongo_res_q.put([ip,ip_info])



def main():

    print 'start:  ', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    # 获取IP
    get_ips()
    get_state_td = []
    for _ in range(thread_num):
        get_state_td.append(threading.Thread(target=get_ip_state))
    for td in get_state_td:
        td.start()
    time.sleep(50)
    print 'save ip info ...\n'
    mysql_save_db_td = threading.Thread(target=mysql_save_res)
    mysql_save_db_td.start()
    mongo_save_db_td = threading.Thread(target=mongo_save_res)
    mongo_save_db_td.start()
    mysql_save_db_td.join()
    mongo_save_db_td.join()
    print 'end:   ', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))


if __name__ == '__main__':
    main()
    # get_ip_state(ip)
