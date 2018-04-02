
-- data
item             item_type          domain_count   update_time   domain_count_info
1API GmbH	sponsoring_registrar	227	2018-03-28 15:14:20	Porno:58;Gamble:167;Illegal:2;
22NET, INC.	sponsoring_registrar	212	2018-03-28 15:14:20	Gamble:201;Illegal:3;Porno:8;
35 Technology Co., Ltd.	sponsoring_registrar	5	2018-03-28 15:14:20	Porno:1;Gamble:4;
abcdomain (ABCDomain LLC)	sponsoring_registrar	6	2018-03-28 15:14:20	Gamble:6;

假设要查找Gamble类型并排序：核心 substring(str,pos,len)截取子串
1 在domain_count_info中找到'Gamble:' 的结尾':'locate('Gamble:',domain_count_info,1) + length('Gamble:')
2 找到'Gamble:167;'结尾';'的位置：locate(';',domain_count_info,locate('Gamble',domain_count_info,1))
3 计算2中';'的位置 与 1中':' 位置的差
4 根据1,2,3,使用substring函数
select item,substring(domain_count_info,\
      locate('Gamble:',domain_count_info) + length('Gamble:'),\
      locate(';',domain_count_info,locate('Gamble:',domain_count_info)) - locate('Gamble:',domain_count_info) - length('Gamble:')) as typenum
from reg_info
where domain_count_info like '%Gamble%'
order by typnum + 0;
