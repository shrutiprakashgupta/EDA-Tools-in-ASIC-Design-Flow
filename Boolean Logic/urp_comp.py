# Unate Recursive Paradigm Complement 
import numpy as np

def most_binate(c):
    #Selecting the most binate
    a = np.sum(abs(c),0)
    s = np.sum(c,0)
    binate = np.where(a!=abs(s))[0]
    if(np.size(binate)):
        x = np.where(abs(s)==np.min(abs(s[binate])))[0]
        for i in x:
            if(i in binate):
                return i
    else:
        x = np.where(a==np.max(a))[0][0]
        return x
        
def nothing(n):
    #Complement is don't care 
    print('['+'11 '*(n-1)+'11]')
    exit(0)
    return 0

def get_cubelist(f,n,m):
    #n is number of boolean variables
    #m is number of product terms in the SOP
    if(n>0):
        if(m>0):
            temp = [f[i].split(" ") for i in range(2,len(f))]
            temp = [[t for t in temp[i] if t] for i in range(len(temp))]
            if(len(temp)==1):
                if(temp[0][0]=='0'):
                    #Empty cube 
                    nothing(n)
            c = np.zeros((m,n))
            for i in range(m):
                for x in temp[i][1:]:
                    c[i,abs(int(x))-1] = int(x)/abs(int(x))
            return c

def pos_cofactor(c,x):
    p = np.copy(c)
    i = 0
    while(i<np.size(p,0)):
        if(p[i,x]<0):
            p = np.delete(p,i,0)
            i = i-1
        else:
            p[i,x] = 0
        i = i+1
    return p

def neg_cofactor(c,x):
    n = np.copy(c)
    i = 0
    while(i<np.size(n,0)):
        if(n[i,x]>0):
            n = np.delete(n,i,0)
            i = i-1
        else:
            n[i,x] = 0
        i = i+1
    return n

def merge_cofactor(x,c,v):
    for i in range(np.size(c,0)):
        c[i,x] = v
    return c
    
def splash(p,n):
    if(p.size==0):
        return n
    elif(n.size==0):
        return p
    else:
        c = np.concatenate((p,n),axis=0)
        return c

def cubelist_comp(c,n):
    if(c.size==0):                                      #if c is 0
        return np.zeros((1,n))
    elif(np.min(np.count_nonzero(c,axis=1))==0):        #if c is 1
        return np.array([])
    elif(np.size(c,0)==1):                              #if c is simple
        cares = np.nonzero(c[0])[0] 
        output = np.zeros((np.size(cares),np.size(c)))
        for i in range(len(cares)):
            output[i,cares[i]] = -1*c[0][cares[i]]
        return output
    else:                                               #if c is complex
        x = most_binate(c)
        # print("The most binate variable is: "+str(x))
        xp = pos_cofactor(c,x)
        xn = neg_cofactor(c,x)
        #Iterate on Positive and Negative Cofactors
        xp = cubelist_comp(xp,n)
        xn = cubelist_comp(xn,n)
        xp = merge_cofactor(x,xp,1)
        xn = merge_cofactor(x,xn,-1)
        #Merging back the two cofactors
        output = splash(xp,xn)
        return output 

f = open("input.pcn","r")                              #The original input file contains the logic in PCN
f = f.read().split("\n")
n = int(f[0])
m = int(f[1])
c = get_cubelist(f,n,m)                                #Converting pcn to matrix notation 
print("The original cubelist is: ")
print(c)
input()

x = cubelist_comp(c,n)
print("The unoptimized complement is: ")
print(x)
input()

#Optimization using the Absorption laws
x = np.append(x,np.reshape(np.count_nonzero(x,axis=1),(np.size(x,0),1)),axis=1)
x = np.array([sorted(x, key=lambda x:x[-1])[i] for i in range(len(x))])
n_terms = set(x[:,-1])                                                                                                                                                                                                                                                                                                                                                                       
i = 0
while(i < np.size(x,0)):
    flag = 0
    j = i+1
    while(j < np.size(x,0)):
        differ = np.count_nonzero(x[i][:-1]!=x[j][:-1])
        if(differ == (x[j][-1]-x[i][-1])):     
            # print("0>"+str(i)+" "+str(j))
            # input()
            # Debug output
            x = np.delete(x,j,0)
            flag = 1
        elif(differ == (x[j][-1]-x[i][-1]+1)):
            # print("1>"+str(i)+" "+str(j))
            # input()
            # Debug output
            x[j,np.where(abs(x[j,:-1]-x[i,:-1])==2)] = 0
            x[j,-1] = x[j,-1]-1
            flag = 1
        j = j+1
    if(flag):
        #If any change, proceed to the next iteration 
        i = 0
        x = np.array([sorted(x, key=lambda x:x[-1])[i] for i in range(len(x))])
    else:
        i = i+1
        
print("The optimized Boolean Complement is: ")
print(x[:,:-1])
