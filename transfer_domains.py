#coding=utf-8
import MySQLdb


# conn = MySQLdb.connect('172.29.152.249', 'root', 'platform', 'mds_new', charset = 'utf8')
# cur = conn.cursor()
# sql = "SELECT domain,maltype FROM mal_domain_collect WHERE maltype = '非法赌博' LIMIT 90000"
# count = cur.execute(sql)
# print count
# res = cur.fetchall()
# cur.close()
# conn.close()

with open('white_list.txt','r') as f:
    res = f.readlines()


conn = MySQLdb.connect('172.26.253.3', 'root', 'platform', 'mal_domain_profile', charset = 'utf8')
cur = conn.cursor()
source = 1
for item in res:
    domain = item.strip()
    sql = "INSERT INTO white_list(domain) VALUES('%s');" %(domain)
    print sql
    cur.execute(sql)
conn.commit()
cur.close()
conn.close()
