# encoding:utf-8
"""
    icp分析

    author：csy
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mysql_operation

'''数据库连接'''
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')

def page_recheck():
    """
    page_icp查重分析
    """
    pass



def icp_cmp():
    """
    icp比对：
    1. auth_icp无，page_icp无  -- 无ICP备案信息
    2. auth_icp无，page_icp有  -- 页面显示虚假ICP备案信息(实际无备案)
    3. auth_icp有，page_icp有，且相同 -- 页面显示真实ICP信息
    4. auth_icp有，page_icp有，且相同 -- 页面显示真实ICP信息(实际有备案)
    5. auth_icp×，page_icp -1 -- 页面ICP无法获取

    auth_icp 的两类取值：icp，--
    page_icp 的三类去值：icp，-1,--
    """
    sql = "SELECT domain,auth_icp,page_icp FROM domain_icp;"
    fetch_data = mysql_conn.exec_readsql(sql)
    for item in fetch_data:
        domain,auth_icp,page_icp = item
        # print domain,auth_icp,page_icp
        icp_cmp_res = get_icp_cmp_res(auth_icp,page_icp)
        print domain,icp_cmp_res
        sql = "UPDATE domain_icp SET icp_tag = '%s', flag = flag + 4 WHERE domain = '%s'" %(icp_cmp_res,domain)
        exec_res = mysql_conn.exec_cudsql(sql)
    mysql_conn.commit()



def get_icp_cmp_res(auth_icp,page_icp):
    """
    icp比对：
    1. auth_icp无，page_icp无  -- 无ICP备案信息
    2. auth_icp无，page_icp有  -- 页面显示虚假ICP备案信息(实际无备案)
    3. auth_icp有，page_icp无 -- 页面未显示ICP(实际有备案)
    4. auth_icp有，page_icp有，且相同 -- 页面显示真实ICP信息
    5. auth_icp有，page_icp有，且不同 -- 页面显示虚假ICP信息(实际有备案)
    6. auth_icp×，page_icp -1 -- 页面ICP无法获取

    auth_icp 的两类取值：icp，--
    page_icp 的三类去值：icp，-1,--

    """
    if page_icp == '-1':
        return '页面ICP无法获取'
    elif auth_icp == '--' and page_icp == '--':
        return '无ICP备案信息'
    elif auth_icp == '--' and page_icp != '--':
        return '页面显示虚假ICP备案信息(实际无备案)'
    elif auth_icp != '--' and page_icp != '--':
        return '页面未显示ICP(实际有备案)'
    elif auth_icp == page_icp:
        return '页面显示真实ICP信息'
    else:
        return '页面显示虚假ICP信息(实际有备案)'





if __name__ == '__main__':
    icp_cmp()
