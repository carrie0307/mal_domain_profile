# coding:utf-8


import time
from selenium import webdriver
import Queue
import threading
import re
import os
import datetime
import common
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mysql_operation

'''同步队列'''
domain_q = Queue.Queue()
html_q = Queue.Queue()
icp_q = Queue.Queue()

domains_q = Queue.Queue()
html_q = Queue.Queue()
res_q = Queue.Queue()

driver_path = "/usr/local/phantomjs-2.1.1-linux-x86_64/bin/phantomjs"


'''数据库连接'''
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')

'''线程数量'''
thread_num = 5


def get_domains():
    '''
    功能:从数据库中读取未获取权威腾讯检测结果的域名，添加入域名队列
    '''
    global mysql_conn

    sql = "SELECT domain FROM domain_auth_detect WHERE flag = 0;"
    fetch_data = mysql_conn.exec_readsql(sql)
    if fetch_data == False:
        print "获取数据有误..."
        return False
    for domain in fetch_data:
        domain_q.put(domain[0])



def kill_process():
    '''
    杀掉phantomjs的进程
    '''
    print 'kill processes ...\n'
    r = os.popen("ps -ef|grep 'phantomjs' |grep -v grep |awk '{print $2}'") # 获取执行结果
    text = r.read()
    r.close()
    pids = text.split('\n')
    for pid in pids:
        cmd = "kill " + pid
        print cmd
        os.system(cmd)



def phantomjs_get_html(driver,domain):
    '''
    通过phantomjs获取判断结果的页面
    '''
    driver.get("https://guanjia.qq.com/online_server/webindex.html")
    driver.find_element_by_id('search_site').clear()
    driver.find_element_by_id("search_site").send_keys(domain)
    driver.find_element_by_id("search_button").click()
    time.sleep(3)
    # driver.implicitly_wait(10) # 隐式等待10s
    page = driver.page_source
    return page


def get_judge_res():
    '''
    从判断将结果页面中获取判断结果
    若获得结果则返回，反之返回None，再异常处理中再获取一遍
    # <span class="loading_score danger">危险&nbsp;-&nbsp;您要访问的网站包含非法赌博信息</span>
    # <span class="loading_score safe">安全网站</span>
    '''
    global html_q
    global res_q

    while True:
        domain,page = html_q.get(timeout = 100)

        qq_judge = re.compile(r'<span class="loading_score .+?">(.+?)</span>').findall(page)
        if qq_judge: # 未提取到的可能是页面未加载完全，先不存储
            qq_judge_res = qq_judge[0]
            qq_judge_res.replace('&nbsp','--')
            res_q.put([domain,qq_judge_res])

        """另外一种提取方法"""
        # from lxml import etree加上引用
        # page = etree.HTML(driver.page_source)
        # res = page.xpath('//*[@id="score_img"]/span/text()')
        # if res:
        #     # qq_judge_res = common.unicode2zh(res[0])
        #     print domain,res[0]
        # else:
        #     with open('qq_anomalous.txt','r') as f:
        #         f.write(page)
        # img = str(str(url).split('/')[-1]) # 获取图片名称（编号）
        # qq_judge = webscan_map[img]
        # return url


def save_res():
    """

    """
    global res_q
    global mysql_conn
    counter = 0

    while True:

        try:
            domain,detect_res = res_q.get(timeout=200)
        except Queue.Empty:
            print 'save over ... \n'
            break
        # print domain, detect_res

        insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "UPDATE domain_auth_detect SET qq_res = '%s',qq_insert_time = '%s',flag = flag + 1 WHERE domain = '%s';" %(detect_res,insert_time,domain)
        print domain,insert_time,detect_res
        exec_res = mysql_conn.exec_cudsql(sql)
        if exec_res:
            counter += 1
            print "counter:" + str(counter)
            if counter == 100:
                mysql_conn.commit()
                counter = 0
        else:
            res_q.put([domain,detect_res])
    mysql_conn.commit()
    print "存储完成... "





def get_html_handler(driver):
    """
    调用phantomjs_get_html(driver,domain)利用无头浏览器发送域名，获取页面
    """

    global domain_q,html_q
    global driver_path

    while not domain_q.empty():
        domain = domain_q.get()
        # 打开腾讯首页，发送域名
        try:
            page_html = phantomjs_get_html(driver,domain)
        except:
            # 出现异常则关闭浏览器
            driver.quit()
            # 关闭后重新打开一个新的浏览器
            driver = webdriver.PhantomJS(executable_path = driver_path)
            print "打开新的浏览器... "
            continue

        html_q.put([domain,page_html])

    driver.quit()
    print '页面全部获取完成...'


def main():
    get_domains()

    get_html_td = []
    for _ in range(thread_num):
        driver = webdriver.PhantomJS(executable_path = driver_path)
        get_html_td.append(threading.Thread(target=get_html_handler,args=(driver,)))

    for td in get_html_td:
        td.start()

    get_res_td = threading.Thread(target=get_judge_res)
    get_res_td.start()

    print 'saving ...'
    save_res_td = threading.Thread(target=save_res)
    save_res_td.start()
    save_res_td.join()

    mysql_conn.close_db()
    kill_process()


if __name__ == '__main__':
    main()
    # get_domains()

    # get_html_td = []
    # for _ in range(thread_num):
    #     driver = webdriver.PhantomJS(executable_path = driver_path)
    #     get_html_td.append(threading.Thread(target=get_html_handler,args=(driver,)))
    #
    # for td in get_html_td:
    #     td.start()
    #
    # get_res_td = threading.Thread(target=get_judge_res)
    # get_res_td.start()
    # get_res_td.join()

    # kill_process()
