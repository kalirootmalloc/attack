#!/usr/bin/python
# -*- coding: UTF-8 -*-
import smtplib
import email.mime.multipart
import email.mime.text
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
 
#send email
#refer to https://www.runoob.com/python/python-email.html
#refer to https://www.cnblogs.com/zhangxinqi/p/9113859.html
def send_email(smtp_host, smtp_port, sendAddr, password, recipientAddrs, subject='', content=''):
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
    msg['from'] = sendAddr
    msg['to'] = recipientAddrs
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
    sendfile = MIMEApplication(open(r'/root/Desktop/filezip/linux.zip', 'rb').read())
    sendfile.add_header('Content-Disposition', 'attachment', filename="linux.zip")  
    #为附件添加一个标题
    msg.attach(sendfile)
 
    try:
        smtpSSLClient = smtplib.SMTP_SSL(smtp_host, smtp_port)  # 实例化一个SMTP_SSL对象
        loginRes = smtpSSLClient.login(sendAddr, password)  # 登录smtp服务器
        print(f"登录结果：loginRes = {loginRes}")  # loginRes = (235, b'Authentication successful')
        if loginRes and loginRes[0] == 235:
            print(f"登录成功，code = {loginRes[0]}")
            smtpSSLClient.sendmail(sendAddr, recipientAddrs, str(msg))
            print(f"mail has been send successfully. message:{str(msg)}")
            smtpSSLClient.quit()
        else:
            print(f"登陆失败，code = {loginRes[0]}")
    except Exception as e:
        print(f"发送失败，Exception: e={e}")
 
 
try:
    subject = 'find_zip'
    content = 'zipfile has been found'
    send_email('smtp.qq.com', 465, '2689825303@qq.com', 'pgznkwstwhmfdgje', '399982971@qq.com', subject, content)
except Exception as e:
    #print(e)
    pass
 #pgznkwstwhmfdgje