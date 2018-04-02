#coding=utf-8
from pymongo import *

class MongoConn(object):

    def __init__(self, *args, **kwargs):
        """
        initializate database connect
        args:host,db
        """
        self.conn = MongoClient(args[0],27017)
        self.db = self.conn[args[1]]

    def mongo_insert(self,collection_name,documents):
        '''
        mongo插入操作
        '''
        self.collection = self.db[collection_name]
        if isinstance(documents,dict):
            self.collection.insert_one(documents)
        else:
            self.collection.insert_many(documents)

    def mongo_read(self,collection_name,condition,return_parameter,limit_num):
        '''
        mongo读操作
        '''
        self.collection = self.db[collection_name]
        if limit_num:
            res = self.collection.find(condition,return_parameter).limit(limit_num)
        else:
            res = self.collection.find(condition,return_parameter)
        return list(res)


    def mongo_update(self,collection_name,condition,operation,multi_flag=True):
        '''
        mongo更新操作
        '''
        self.collection = self.db[collection_name]
        self.collection.update(condition,{'$set':operation})


    def mongo_inc(self,collection_name,condition,operation):
        '''
        mongo $inc操作
        db.products.update({ sku: "abc123" },{$inc: { quantity: -2 ,size: 1} } 给满足sku: "abc123"的quantity值-2,size的值+1)
        '''
        self.collection = self.db[collection_name]
        self.collection.update(condition,{'$inc':operation})


    def mongo_addtoset(self,collection_name,condition,operation):
        '''
        mongo $addtoset操作（会自动去重）

        向id=2的记录的tags中加入[ "camera", "electronics", "accessories" ]
        db.inventory.update(
                               { _id: 2 },
                               { $addToSet: { tags: { $each: [ "camera", "electronics", "accessories" ] } } }
                            )
        '''
        self.collection = self.db[collection_name]
        self.collection.update(condition,{'$addToSet':operation})

    def mongo_push(self,collection_name,condition,operation):
        '''
        mongo $addtoset操作（不去重） 注：还可以用于添加字典
        db.students.update(
               { name: "joe" },
               { $push: { scores: { $each: [ 90, 92, 85 ] } } }
            )
        '''
        self.collection = self.db[collection_name]
        self.collection.update(condition,{'$push':operation})

    def mongo_any_update(self,collection,condition,operation):
        '''
        任何类型 mongo 的更新操作，operation中需要自己包括更新的类型
        '''
        self.collection = self.db[collection]
        self.collection.update(condition,operation)

    def mongo_any_update_new(self,collection,condition,operation,upsert):
        '''
        任何类型 mongo 的更新操作，operation中需要自己包括更新的类型
        '''
        self.collection = self.db[collection]
        self.collection.update(condition,operation,upsert)


if __name__ == '__main__':
    mongo_conn = MongoConn('172.29.152.152','mal_domain_min')
    print mongo_conn.mongo_read('domain_index',{},{'_id':False,'domain':True})
    # client = MongoClient('172.29.152.152', 27017)
    # db = client.mal_domain_min
    # collection = db.domain_index
    # res = collection.find({},{'_id':False,'domain':True})
    # print list(res)
    # mongo_conn.mongo_update('domain_index',{'domain':'0-360c.com'},{'whois_flag':1},True)
