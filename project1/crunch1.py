import random
import itertools as its
import sys

def isDup(strs):

    hashTable = dict()

    listStrs = list(strs)

    i = 0

    while i < len(strs):

        if listStrs[i] in hashTable:

            #print("有重复字符")

            return True

        else:

            hashTable[listStrs[i]] = None

        i += 1

        if i >= len(strs):

            #print("没用重复字符")

            return False







def help():
    if len(sys.argv)==4 and isinstance(sys.argv[1],str) :
        #print("is ok")
        return
    else:
        #print(len(sys.argv)==4,isinstance(sys.argv[1],str),isinstance(int(sys.argv[2]),int),isinstance(sys.argv[3],int))
        print("example crunch.py '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'  1 4")
        exit(0)
#0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&'()*+,-./:;<=>?@[]^_`{|}~
if __name__=='__main__':
    #print(type(sys.argv[1]),sys.argv[1])
    #print(type(sys.argv[2]),sys.argv[2])
    #print(type(sys.argv[3]),sys.argv[3])

    #its.product()
    #Dictor(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]))
    #print(len(sys.argv),sys.argv)
    help()
    dic=open('password_big00.txt','w')
    CSet=sys.argv[1]
    minlen=int(sys.argv[2])
    maxlen=int(sys.argv[3])
    is_quchong=True

    if   maxlen>minlen:
        minlen=minlen
        maxlen=maxlen
    else:
        minlen=maxlen
        maxlen=minlen
    for num in range(minlen,maxlen+1):
        #print("num",num)
        #input()
        keys=its.product(CSet,repeat=num)
        print(keys)
        #print('hello')
        for key in keys:
            if is_quchong and not isDup(key):
                #print("17"+"".join(key)+"\n")
                dic.write("".join(key)+'\n')

    dic.close()