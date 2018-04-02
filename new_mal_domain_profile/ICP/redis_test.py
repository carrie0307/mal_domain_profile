# coding=utf-8
import redis

r = redis.Redis(host='10.245.146.81', port=6379)
print r.llen("ip_list")
print r.lpop("ip_list")
print r.llen("ip_list")
