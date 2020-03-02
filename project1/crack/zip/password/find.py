index1='188 243 972 278 166 541 256 944 804 207'
index2=index1.split()
index3=[int(i) for i in index2]
f=open('password1.txt')
t1=f.readlines()
end=''
for i in index3:
    #print(type(i),i)
    t2=t1[int((i)/4-1)]
    t3=t2.split()
    t4=t3[(i-1)%4]
    end+=t4
    print(t4)
print(end)
