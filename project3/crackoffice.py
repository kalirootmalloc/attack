# -*-coding:utf-8-*-

import zipfile
import datetime
import optparse
import sys
import msoffcrypto

from threading import Thread

from tqdm import tqdm

from tqdm._tqdm import trange

start =datetime.datetime.now()

#zFile = zipfile.ZipFile("evil.zip")

#zFile.extractall(pwd=secret)

is_found=False
ppp=open('aimpassword.txt','w')
def extractFile(msfile,passwords_arr):

	'''

	破解方法

	:param zfile:需要破解的文件

	:param password:尝试代码

	:return:

	'''

	global is_found
	global start
	global ppp
	
	bar = tqdm(passwords_arr)
	index=0
	for letter in bar:
		line =passwords_arr[index]
		
		#bar.set_description("Processing %s"%letter)
		#bar.set_description(letter)
		index+=1
		password1 = line.strip('\n')

		

	#如果口令正确，输出口令，如果错误，抛出异常并测试下一个口令

		if is_found==True:

			

			return

		try:

			#print(password1)

			msfile.load_key(password=password1)

			msfile.decrypt(open('decrypto'+zname,'wb'))

			is_found=True
			ppp.write(password1)
			sys.stdout.flush()
			print("Found Password:",password1)
			end = datetime.datetime.now()
			print("程序运行时间："+str((end-start).seconds)+"秒")
			#event.set()

			return

		except:

			#event.wait()

			# if password=='7j9STupy':

			# 		print("7j9STupy")

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

	print(zname,type(zname))

	msfile = msoffcrypto.OfficeFile(open(zname,"rb"))#实例化类

	passFile = open(dname)#打开字典文件

	room=passFile.readlines()



	threads_num=8#确认线程数

	arr=[]

	for i in range(threads_num):



		tag=int(len(room)/threads_num)

		if i!=threads_num-1:

			arr=(room[i*tag:(i+1)*tag])

		else:

			arr=(room[i*tag:])
		is_begin=True
		
		while is_begin:
			try:
				#print('thread '+str(i)+'is start')
				t = Thread(target=extractFile,args=(msfile,arr))

				t.start()
				#t.join()
				is_begin=False
				time.sleep(0.1)
			except:

				is_begin=True








 

if __name__=='__main__':

	#event = threading.Event()

	main()

