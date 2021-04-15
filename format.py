a='''
##Comment Ratio Target
def comment_ratio_target(filetext,crt):
    a=filetext
    total_length=len(a.split("\n"))
    comment_length=0
    empty_lines=0
    for i in a:    
        if(i.strip(' ').startswith("#")):        
            comment_length+=1    
        elif(i.strip(' ').startswith(("'''", '"""'))):        
            comment_length+=1    
        if(i.strip(' ').startswith('\n') or len(i.strip(" "))==0):        
            empty_lines+=1
    total_length=total_length-empty_lines    
    result=(comment_length/total_length)*100
    return result


def func(p):    
    comment_length=0    
    for i in p:        
        if(i.strip(' ').startswith("#")):            
            comment_length+=1        
        elif(i.strip(' ').startswith(("'''", '"""'))):            
            comment_length+=1    
    return comment_length
##Comment Density
def comment_density(filetext,comment_density):
    a=comment_density
    b=100//a
    a=filetext
    total_length=len(a)
    i=0
    li=[]
    flag=0
    while(i<len(a)-b):    
        split_a=a[i:i+b]    
        com=func(split_a)    
        if(com==1):        
            flag=1    
        else:        
            flag=0        
            break    
        i+=b
    if(flag==0):    
        print("Code Density is not satisfied")
    else:    
        print("Code Density is Satisfied")
'''

print(a.replace(" "," "))
