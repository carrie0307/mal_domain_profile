#coding=utf-8
import MySQLdb
from pymongo import *


conn = MySQLdb.connect('172.26.253.3', 'root', 'platform', 'mal_domain_profile', charset = 'utf8')
cur = conn.cursor()
sql = "SELECT domain,maltype FROM domain_index WHERE source = '2nd_domains' LIMIT 10;"
count = cur.execute(sql)
res = cur.fetchall()
documents = []
for item in res:
    domain,maltype = item
    temp = {'domain':domain, 'maltype':maltype,'domain_ip_cnames':[],'visit_times':0.0,'change_times':0.0}
    documents.append(temp)

conn = MongoClient('172.29.152.151',27017)
db = conn.new_mal_domain_profile
collection = db['domain_ip_cname_test']
collection.insert_many(documents)
