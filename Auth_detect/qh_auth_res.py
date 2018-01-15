# encoding:utf-8
"""
    从http://webscan.360.cn/index/checkwebsite?url=baidu.com获取检测结果
"""


import time
from selenium import webdriver
from selenium.webdriver.common.proxy import ProxyType
import Queue
import threading
import chardet
from lxml import etree
import os
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mysql_operation

'''同步队列'''
domain_q = Queue.Queue()
html_q = Queue.Queue()
res_q = Queue.Queue()

driver_path = "/usr/local/phantomjs-2.1.1-linux-x86_64/bin/phantomjs"


'''数据库连接'''
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')

'''线程数量'''
thread_num = 1

url = "http://webscan.360.cn"


# domain = '520820.com'
# driver = webdriver.PhantomJS(executable_path="/usr/local/phantomjs-2.1.1-linux-x86_64/bin/phantomjs")
# url = 'http://webscan.360.cn/index/checkwebsite?url=' + domain
# driver.get(url)
# page = driver.page_source
# page = etree.HTML(page)
# res = page.xpath('//*[@id="jg_tips"]/text()')
# if res:
#     print domain,res[0]
# driver.quit()

def get_domains():
    '''
    功能:从数据库中读取未获取权威360检测结果的域名，添加入域名队列 # FLAG=1
    腾讯结果获取完后，获取360的结果，因此flag=1
    '''
    global mysql_conn

    sql = "SELECT domain FROM domain_auth_detect WHERE flag =1 LIMIT 100;"
    fetch_data = mysql_conn.exec_readsql(sql)
    if fetch_data == False:
        print "获取数据有误..."
        return False
    for domain in fetch_data:
        domain_q.put(domain[0])


def get_source_page_handler(driver):
        """
        调用get_source_page(driver,domain)利用无头浏览器发送域名，获取页面
        """
        global domain_q,html_q
        global driver_path
        global url

        while not domain_q.empty():
            domain = domain_q.get()
            # 打开腾讯首页，发送域名
            try:
                page_html = get_source_page(driver,domain)
            except:
                # 出现异常则关闭浏览器
                driver.quit()
                # 关闭后重新打开一个新的浏览器
                driver = webdriver.PhantomJS(executable_path = driver_path)
                driver.get(url)
                print "打开新的浏览器... "
                continue
            html_q.put([domain,page_html])

        driver.quit()
        print '页面全部获取完成...'



def get_source_page(driver,domain):
    """
    通过phantomjs的driver获取页面源代码
    """
    driver.find_element_by_id('url').clear()
    driver.find_element_by_id("url").send_keys(domain)
    driver.find_element_by_xpath("/html/body/div[1]/div[5]/div[2]/div/div[1]/div/form/span").click()
    time.sleep(5) # 页面加载时间
    page = driver.page_source
    return page


def get_judge_res():
    '''
    从判断将结果页面中获取判断结果
    若获得结果则返回，反之返回None，再异常处理中再获取一遍
    '''
    global html_q
    global res_q

    while True:
        domain,source_page = html_q.get(timeout = 600)
        page = etree.HTML(source_page)
        res = page.xpath('//*[@id="jg_tips"]/text()')
        if res:
            if res[0] != '...':
                qh_judge_res = res[0]
            else:
                qh_judge_res = '网站还未认领，无法进行漏洞检测，安全得分未知'
            res_q.put([domain,qh_judge_res])
        elif '访问网站方式太像一个机器人' in str(source_page):
            print domain
            print '未提取到结果'
        else:
            print 'get res blank ...'
        # 如果没有提取到结果，则不返回结果，最终数据库标志位不变


def save_res():
    """
    存储结果
    """
    global res_q
    global mysql_conn
    counter = 0

    while True:

        try:
            domain,detect_res = res_q.get(timeout=800)
        except Queue.Empty:
            print 'save over ... \n'
            break
        # print domain, detect_res

        insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "UPDATE domain_auth_detect SET qh_res = '%s',qh_insert_time = '%s',flag = flag + 2 WHERE domain = '%s';" %(detect_res,insert_time,domain)
        print domain,insert_time,detect_res
        exec_res = mysql_conn.exec_cudsql(sql)
        if exec_res: # 说明语句执行成功
            counter += 1
            print "counter:" + str(counter)
            if counter == 100:
                mysql_conn.commit()
                counter = 0
        else:
            # 执行不成功先把结果加入队列（这里主要考虑到可能由于死锁而无法更新此记录的信息，因此先加入队列，留待以后处理）
            res_q.put([domain,detect_res])
    mysql_conn.commit()
    print "存储完成... "


def main():
    get_domains()
    global url

    get_html_td = []
    for _ in range(thread_num):
        driver = webdriver.PhantomJS(executable_path = driver_path)
        driver.get('http://webscan.360.cn/index/checkwebsite?url=baidu.com')
        get_html_td.append(threading.Thread(target=get_source_page_handler,args=(driver,)))

    for td in get_html_td:
        td.start()

    get_res_td = threading.Thread(target=get_judge_res)
    get_res_td.start()

    print 'saving ...'
    save_res_td = threading.Thread(target=save_res)
    save_res_td.start()
    save_res_td.join()

    mysql_conn.close_db()
    os.system('./kill_phan.sh')


if __name__ == '__main__':
    main()

    # domain = '000023.com'
    # driver = webdriver.PhantomJS(executable_path="/usr/local/phantomjs-2.1.1-linux-x86_64/bin/phantomjs")

    # proxy=webdriver.Proxy()
    # proxy.proxy_type=ProxyType.MANUAL
    # proxy.http_proxy='118.193.107.92:80'
    # #将代理设置添加到webdriver.DesiredCapabilities.PHANTOMJS中
    # proxy.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)
    # driver.start_session(webdriver.DesiredCapabilities.PHANTOMJS)

    # start = time.time()
    # print '----'
    # url = 'http://webscan.360.cn/index/checkwebsite?url=baidu.com'
    # # url = 'http://webscan.360.cn/'
    # driver.get(url)
    # print '!!!!'
    # driver.find_element_by_id('url').clear()
    # driver.find_element_by_id("url").send_keys(domain)
    # driver.find_element_by_xpath("/html/body/div[1]/div[5]/div[2]/div/div[1]/div/form/span").click()
    # print '@@@'
    # time.sleep(3)
    # source_code = driver.page_source
    # print '***'
    # page = etree.HTML(source_code)
    # # print source_code
    # res = page.xpath('//*[@id="jg_tips"]/text()')
    # if res:
    #     print domain,res[0]
    # elif '访问网站方式太像一个机器人' in str(source_code):
    #     print '-----'
    # print '===='
    # driver.quit()
    # end = time.time()
    # print end - start
