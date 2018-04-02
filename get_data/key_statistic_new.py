# -*- coding: utf-8 -*-

from Base import Base

class KeyWhoisStatistic(Base):
    """
    域名WHOIS关键信息统计类
    """
    def __init__(self):
        Base.__init__(self)

    def keywhois(self, key_source, top_n, maltype=None, has_all=False):
        """
        获取注册商/注册者/注册电话/注册邮箱的非法域名数量统计结果
        :param key_source:registrar/reg_email/reg_phone/reg_name （注册商/注册者/注册电话/注册邮箱）
        :param top_n: 查询topn条记录,当top_n=-1时取所有记录
        :param maltype:选择恶意类型Gamble/Prono 或不选
        :param has_all:True=>查询域名总数+色情类域名数+赌博类域名数,False=>查询域名总数或色情类域名数/赌博类域名数
        :return: 返回形式 [{序列：序列号,查询源:查询源值,域名数量：数量值},{序列：序列号,查询源:查询源值,域名数量：数量值},...]
        """
        if top_n == -1:
            maxm = 100  # 无穷大数
            top_n = maxm

        if not has_all:
            if maltype is not None:
                if maltype == 'Gamble':
                    cout = "gamble_count"
                elif maltype == 'Porno':
                    cout = "porno_count"
                else:
                    print "出现新恶意类型，请添加"
                    return None
            else:
                cout = "domain_count"
            cout = cout + " as num"
        else:
            cout = " domain_count,gamble_count,porno_count "

        # if key_source == 'registrar':
        #     table_name = 'domain_registrar'
        #
        #     select_sql = "select domain_registrar_name as registrar," + cout + " from " + table_name \
        #                  + " where domain_registrar_name!= '' order by domain_count desc limit 0," + str(top_n)
        # elif key_source in ['reg_email', 'reg_phone', 'reg_name']:
        #     table_name = 'reg_info'
        #     select_sql = "select item as " + key_source + "," + cout + " from  " + table_name + " where reg_type='" + key_source \
        #                  + "' and item!='' order by domain_count desc limit 0," + str(top_n)

        print 'key: ', key_source
        if key_source in ['reg_email', 'reg_phone', 'reg_name','sponsoring_registrar']:
            table_name = 'reg_info'
            select_sql = "select item as " + key_source + "," + cout + " from  " + table_name + " where reg_type='" + key_source \
                         + "' and item!='' order by domain_count desc limit 0," + str(top_n)
        else:
            print "源选择错误，请重新选择源registrar/reg_email/reg_phone/reg_name"
            return None

        results = self.mysql_db.query(select_sql)

        return self.add_seq_num(results)

class IPStatistic(Base):
    """
    IP相关信息统计
    """
    def __init__(self):
        Base.__init__(self)

    def ip_baseinfo(self, top_n, maltype=None):
        """
        获取IP的基本信息(IP,服务域名数量,国家，地区，市，运营商，asn,as_owner)
        :param top_n:  查询topn条记录,当top_n=-1时取所有记录
        :return: top_n条记录 [{序列：序列号,字段1:字段值,字段2:字段值},{序列：序列号,字段1:字段值,字段2:字段值},...]
        """
        if top_n == -1:
            maxm = 10000000  # 无穷大数
            top_n = maxm

        if maltype is not None:
            if maltype == 'Gamble':
                cout = "gamble_count"
            elif maltype == 'Porno':
                cout = "porno_count"
            else:
                print "出现新恶意类型，请添加"
                return None
            add_condition = " and " + cout + " >0"
        else:
            cout = "dm_num"
            add_condition = ""

        table_name = "ip_general_list"
        select_sql = "select IP," + cout + " as num,country,region,city,oper as operater,ASN,AS_OWNER from " + table_name \
                     + " where IP!='' " + add_condition + " order by " + cout + "  desc limit 0," + str(top_n)
        results = self.mysql_db.query(select_sql)

        return self.add_seq_num(results)

if __name__ == "__main__":
    kw = KeyWhoisStatistic()
    print kw.keywhois('sponsoring_registrar', -1, has_all=True)
    print kw.keywhois('sponsoring_registrar',-1,maltype='Gamble')
    print kw.keywhois('sponsoring_registrar', 4,maltype='Porno')
    # print kw.keywhois('reg_name', 4)
    # print kw.keywhois('registrar',4)
    # ips = IPStatistic()
    # print ips.ip_baseinfo(5)
    # print ips.ip_baseinfo(5, maltype='Gamble')
