# -*- coding: utf-8 -*-

import torndb
from pymongo import MongoClient
from copy import copy

class Base(object):
    def __init__(self):
        self.mysql_db = torndb.Connection(
            host = "172.26.253.3",
            database = "mal_domain_profile",
            user = "root",
            password = "platform",
            charset = "utf8",
        )
        self.mongo_db = MongoClient('172.29.152.151',27017).new_mal_domain_profile

    def add_seq_num(self,results):

        if isinstance(results,list):
            res = copy(results)
            for i,rs in enumerate(res):
                results[i]['seq_num']=i+1
        else:
            print "结果非列表形式，添加序列号失败"

        return results
