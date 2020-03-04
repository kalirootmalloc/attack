# coding=utf-8
import PyPDF4
import sys
import os
pwd=os.getcwd()+'\\'
#print(pwd)
pdfReader = PyPDF4.PdfFileReader(open('1.pdf','rb'))
print (pdfReader)


if pdfReader.isEncrypted:
    #print('try')
    File = open(pwd+'password2.txt')
    sfile = File.read()
    dic = sfile.split('\n') # dic has 256 lines ; 4 key in 1 line
    num = len(dic)
    for i in range(num):
        for k in range(0,4):
            passwd = str(dic[i]).split()
            #print ((passwd[k]))
            #print('try '+str(i) +' ...')
            if pdfReader.decrypt(passwd[k]):
            
                print('Password has found: ' + passwd[k])
                '''
                #print('PDF有 '+ str(pdfReader.numPages) + '...')
                #print('内容摘要')
                pageObj = pdfReader.getPage(0)
                print(pageObj.extractText())
                break
            
            temp = passwd[k].lower()
            if pdfReader.decrypt(temp):
                print(temp)
                #print('破解成功，密码是 ' + temp + '...')
                #print('PDF有 '+ str(pdfReader.numPages) + '...')
                #print('内容摘要')
                pageObj = pdfReader.getPage(0)
                print(pageObj.extractText())
                break
                '''
       # print('失败')
    print('程序关闭...')
    sys.exit()

