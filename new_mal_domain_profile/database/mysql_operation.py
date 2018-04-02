#/usr/bin/python
#-*- coding: utf-8 -*-
import MySQLdb

class MysqlConn(object):
    """
    每项操作，成功返回True或获取到的数据，反之则为False
    """

    def __init__(self, *args, **kwargs):
        """
        initializate database connect
        args:host,user,passwd,db,charset
        """
        if len(args) == 5:
            self.conn = MySQLdb.connect(
                host=args[0],
                user=args[1],
                passwd=args[2],
                db=args[3],
                charset=args[4]
            )
            self.cur = self.conn.cursor()
            self.flag = True
        else:
            print "parameter error!"
            self.flag = False

    def exec_readsql(self,sql):
        """
        execute sql for READ(SELECT)
        return: data or False
        """
        try:
            count = self.cur.execute(sql)
            if count == 0:
                # print "没有符合条件的数据..."
                return []
            else:
                # print "取回数据 " + str(count) + " 条..."
                fetch_data = self.cur.fetchall()
                return fetch_data
        except Exception,e:
            print sql
            print str(e)
            print "SELECT语句执行有误\n"
            return False


    def exec_cudsql(self, sql):
        """
        execute sql or CREATE/UPDATE/DELETE
        sql
        """
        try:
            self.cur.execute(sql)
            return True
        except Exception, e:
            print sql
            print str(e)
            print "语句执行有误\n"
            return False

    def commit(self):
        """
        commit record
        """
        try:
            self.conn.commit()
            print "commit成功..."
            return True
        except Exception,e:
            print "commit有误..." + str(e)
            return False

    def escape_string(self,string):
        """
        功能：对字符词进行转义
        """
        return MySQLdb.escape_string(string)

    def close_db(self):
        """
        close database
        """
        try:
            self.cur.close()
            self.conn.close()
            print "关闭游标，关闭连接..."
            return True
        except:
            print '关闭游标/连接有误。。。'
            return False

if __name__=="__main__":
    mysql_conn = MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')
    sql = "UPDATE domain_icp SET flag = flag+1, auth_icp = '--' WHERE domain = '00000444.com';"
    mysql_conn.exec_cudsql(sql)
    mysql_conn.commit()
