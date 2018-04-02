# encoding:utf-8
'''
    功能：DNSJ记录存储结果的编码处理

    12930.com的txt记录存储时出现了非utf8字符导致错误，因此这里对整个存储结果进行编码的检查与处理
'''
import chardet

def str_encode_deal(mystr):
	'''
	功能：对字符串的编码处理
	'''
	encode_type = chardet.detect(mystr)['encoding']
	if encode_type:
		if encode_type.find('utf-8') == -1 or encode_type.find('UTF-8') == -1:
			mystr = mystr.decode(encode_type, 'ignore')
	return mystr

def list_enfcode_deal(items):
	'''
	功能：对列表的编码处理
	'''
	for i in range(len(items)):
		if isinstance(items[i], dict):
			dict_encode_deal(items[i])
		elif isinstance(items[i], list):
			list_enfcode_deal(items[i])
		elif isinstance(items[i], tuple):
			# 因为tuple不能赋值，因此先转化为list处理完后再转化为tuple
			items[i] = list(items[i])
			list_enfcode_deal(items[i])
			items[i] = tuple(items[i])
		elif isinstance(items[i],str):
			items[i] = str_encode_deal(items[i])
		else:
			pass


def dict_encode_deal(mydict):
	'''
	功能：对字典的编码处理
	注：由于传入mongo的存储结果是字典，因此这里默认调用dict_encode_deal处理结果
	'''
	# print mydict
	for key, value in mydict.items():
		if isinstance(value, str):
			mydict[key] = str_encode_deal(value)
		elif isinstance(value, list):
			list_enfcode_deal(value)
		elif isinstance(value, tuple):
			# 因为tuple不能赋值，因此先转化为list处理完后再转化为tuple
			value = list(value)
			list_enfcode_deal(value)
			value = tuple(value)
	else:
		pass
