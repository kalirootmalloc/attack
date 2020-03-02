# -*-coding:utf-8-*-
import rarfile
import optparse
from threading import Thread

def extractFile(zFile,password):
	'''
	破解方法
	:param zfile:需要破解的文件
	:param password:尝试代码
	:return:
	'''
	#如果口令正确，输出口令，如果错误，抛出异常并测试下一个口令
	try:

		zFile.extractall(pwd=password.encode('utf-8'))
		print("Found Password:",password)
		#event.set()
		return password
	except:
		#event.wait()
		if password=='7j9STupy':
    			print("7j9STupy")
		pass
 
 
def main():
	'''
	主函数
	'''
	parser = optparse.OptionParser("usage%prog "+"-f <zipfile> -d <dictionary>")
	parser.add_option('-f',dest = 'zname',type = 'string',help = 'specify zip file ')
	parser.add_option('-d',dest = 'dname',type = 'string',help = 'specify dictionary file')
	(options,args) = parser.parse_args()
	if (options.zname == None) | (options.dname == None):
		print(parser.usage)
		exit(0)
	else:
		zname = options.zname
		dname = options.dname
	zFile = rarfile.RarFile(zname)#实例化类
	passFile = open(dname)#打开字典文件
	for line in passFile.readlines():
		'''if event.isSet():
			print "END"
			return
		else:'''
		password = line.strip('\n')
		passwords=password.split()

		for i in passwords:
			#t = threading.Thread(target=extractFile,args=(zFile,password))
			
			t = Thread(target=extractFile,args=(zFile,i))
			t.start()
 
 
if __name__=='__main__':

	main()