# coding=utf-8
'''
    功能： 从页面上获取icp信息

    总有一些提取结果可能不够规范，需要手动修改一些

    -1 打开网页时有误
    -- 页面没有icp
    icp备××× 页面获取到的icp内容

    增加了存储http_code,下次运行前先测试一下
'''

import re
import urllib2
import Queue
import chardet
import StringIO
import threading
import time
import sys
sys.path.append("..") # 回退到上一级目录
import database.mysql_operation

'''数据库连接'''
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')

'''同步队列'''
domain_q = Queue.Queue()
html_q = Queue.Queue()
icp_q = Queue.Queue()

'''线程数量'''
thread_num = 1


def get_domains():
    '''
    功能：从数据库读取未获取页面icp信息的域名
    '''
    global mysql_conn
    sql = "SELECT domain FROM domain_icp WHERE flag < 2;"
    fetch_data = mysql_conn.exec_readsql(sql)
    if fetch_data == False:
        print "获取数据有误..."
        return False
    for domain in fetch_data:
        domain_q.put(domain[0]


# urllib2获取响应可能存在压缩包问题，在此处理；同时处理编码问题
def pre_deal_html(req):
    '''
    功能：urllib2获取响应可能存在压缩包问题，在此处理；同时处理编码问题
    '''
    info = req.info()
    content = req.read()
    encoding = info.getheader('Content-Encoding')
    if encoding == 'gzip':
        buf = StringIO(content)
        gf = gzip.GzipFile(fileobj=buf)
        content = gf.read()
    charset = chardet.detect(content)['encoding']
    if charset != 'utf-8' and charset != None:
        content = content.decode(charset, 'ignore')
    return content


def download_htmlpage():
    '''
    功能：获取网页源代码，添加入html队列

    注： 页面无法访问的，置icp信息为-1
    '''
    global domain_q
    global html_q
    global icp_q
    while not domain_q.empty():
        domain = domain_q.get()
        url = 'http://www.' + domain
        try:
            resp = urllib2.urlopen(url,timeout=20)
            html = pre_deal_html(resp) # 处理编码
            code = resp.code
            html_q.put([domain, html,code])
        except urllib2.HTTPError, e:
            icp_q.put([domain,'-1',code])
            code = e.code
        except Exception, e:
            code = 'WRONG'
            icp_q.put([domain, '-1',code])
            print domain
            print str(e)
    print 'download over ...'


def get_page_icp():
    '''
    功能：获取页面上的icp信息，分三种情况进行处理：
        pattern1: 备案：粤ICP备11007122号-2 (500.com)
        pattern2: 京ICP证 030247号 (icbc) 360soulou.com 豫ICP证041518号
        pattern2: 京ICP证000007 (sina) (这个可能提取会有误)
        pattern3: 粤B2-20090059-111 (qq.com) （增值营业号）
    '''
    global html_q
    global icp_q
    while True:
        try:
            domain,html,code = html_q.get()
        except Queue.Empty:
            print 'get icp info over ...'
            break
        try:
            pattern1 = re.compile(u'([\u4e00-\u9fa5]{0,1}ICP[\u5907][\d]{6,8}[\u53f7]*-*[\d]*)').findall(html)
            if pattern1 != []:
                icp = pattern1[0]
            else:
                pattern2 = re.compile(u'([\u4e00-\u9fa5]{0,1}ICP[\u8bc1].*[\d]{6,8}[\u53f7])').findall(html)
                if pattern2 != []:
                    icp = pattern2[0]
                # 增值业务营业号
                else:
                    pattern3 = re.compile(u'([\u4e00-\u9fa5]{0,1}[A-B][1-2]-[\d]{6,8}-*[\d]*)').findall(html)
                    if pattern3 != []:
                        icp = pattern3[0]
                    else:
                        icp = '--'
            if icp == '':
                icp = '--'
            icp_q.put([domain, icp, code])
        except:
            print domain + "get icp WRONG\n"


def mysql_save_icp():
    """
    向mysql存储页面运行结果
    """
    global icp_q
    global mysql_conn
    counter = 0 # commit计数器

    while True:
        try:
            domain,icp,code = icp_q.get(timeout=200)
        except Queue.Empty:
            print 'save over ... \n'
            break
        print domain, icp
        sql = "UPDATE domain_icp SET flag = flag+2, page_icp = '%s',http_code = '%s' WHERE domain = '%s';" %(icp,code,domain)
        exec_res = mysql_conn.exec_cudsql(sql)
        if exec_res:
            counter += 1
            print "counter : " + str(counter)
            if counter == 1000:
                mysql_conn.commit()
                counter = 0
    mysql_conn.commit()
    print "存储完成... "
    mysql_conn.close_db()



if __name__ == '__main__':
    get_domains()
    get_html_td = []
    for _ in range(thread_num):
        get_html_td.append(threading.Thread(target=download_htmlpage))
    for td in get_html_td:
        td.start()
    print 'get raw html ...\n'
    time.sleep(5)
    print 'get icp ...\n'
    get_icp_td = threading.Thread(target=get_page_icp)
    get_icp_td.start()
    time.sleep(5)
    print 'save icp ...\n'
    save_db_td = threading.Thread(target=mysql_save_icp)
    save_db_td.start()
    save_db_td.join()
