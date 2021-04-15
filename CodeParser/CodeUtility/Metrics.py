import re
import enchant
import math
 
def is_camel_case(s):    
    f= s != s.lower() and s != s.upper() and "_" not in s
    if(f):
        return s +" is in camelcase!"
    else:
        return s+" is not in camelcase!"


def is_pascal_case(s):    
    res = [s[0]]    
    for c in s[1:]:        
        if c in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):            
            res.append('_')            
            res.append(c)        
        else:            
            res.append(c)
    list_of_words = ''.join(res).split('_')    
    d = enchant.Dict("en_US")    
    flag = True     
    for word in list_of_words:
        if(len(word)>0):        
            flag = flag and d.check(word)            
    if(flag):
        return s +" is in Pascalcase!"
    else:
        return s+" is not in Pascalcase!"

def is_hungarian_case(s):    
    res = [s[0]]    
    for c in s[1:]:        
        if c in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):            
            res.append('_')            
            res.append(c)        
        else:            
            res.append(c)
    list_of_words = ''.join(res).split('_')

    
    d = enchant.Dict("en_US")

    flag = True    
    for word in list_of_words[1:]:
        if(len(word)):        
            flag = flag and d.check(word)            
    if(flag):
        return s +" is in Hungariancase!"
    else:
        return s+" is not in Hungariancase!"
#Line Length
def line_length(file_text):
    a=file_text    
    #tolerance=int(input("Enter Tolerance"))
    line_stats=[]    
    count=0    
    flag=False 
    line_len=[]   
    for i in a:
        line_len.append(len(i))  
    return sum(line_len)/len(line_len)
def line_length_details(file_text,max_length):
    a=list(file_text.split('\n'))
    line_stats=[]
    count=0
    for i in a:
        if(len(i)>max_length):                       
            line_stats.append(" Length exceeded and  the line no is "+str(a.index(i)))
            count+=1
                    
    s=''      
    if(count==0):
        return 'No violations of line length'
    else:                             
        s=s+"\n".join(line_stats)
        return s

        

#Function Length
import ast
def func_length(file_text):    
    root = ast.parse(file_text)    
    max_lines=12    
    #tolerance=int(input('Enter Tolerance'))    
    func_length=[]    
    count=0    
    flag=False    
    function_len=[]
    for node in ast.walk(root):        
        if(isinstance(node,ast.FunctionDef)):
            function_len.append(node.end_lineno-node.lineno)
    if(len(function_len)>0):
        return sum(function_len)/len(function_len)
    else:
        return 0

def func_length_details(file_text,max_lines):
    root = ast.parse(file_text)        
    func_length=[]    
    count=0    
    flag=False
    for node in ast.walk(root):        
        if(isinstance(node,ast.FunctionDef)):    
            if(node.end_lineno-node.lineno>max_lines):                
                func_length.append("Violated  number of lines per function in the function named=== "+str(node.name)+'\n')                
            else:
                func_length.append("Satisfied the   number of lines per function in  the function named==="+str(node.name)+'\n')
    return "\n".join(func_length)

               
    

#file Length
import ast
def file_length(file_text):
            
    a=len(file_text.split("\n"))    
    return a

def file_length_details(file_text,max_length):
    a=len(file_text.split("\n"))
    if(a>max_length):        
        return "File length exceeded "    
    else:        
        return "File length is in the limit"



def spellcheck(s):    
    from nltk.corpus import words    
    import nltk
    nltk.download()
    word_list = words.words()    
    word_list.sort(key=len,reverse=True)    
    word_list=list(filter(lambda x:len(x)>1,word_list))
    while(len(s)>0):        
        found=0 
        eng_words=[]       
        for k in range(len(s),-1,-1):                        
            for i in range(len(word_list)):                
                if((s[len(s)-k:len(s)]).lower() == word_list[i]):                    
                    s=s.replace(s[len(s)-k:len(s)],"")                    
                    eng_words.append(word_list[i])                    
                    found=1                    
                    break          
        if(found==0):            
            break 
    if(len(s)>0):
        return {"ne":s,"englishwords":eng_words}
    else:
        return {"englishwords":eng_words}

def varaible_metrics(variable_list):
    result=''
    for i in variable_list:
        if(len(i)>0):
            for j in i:
                if(len(j)>3):
                    
                    
                    cc=is_camel_case(j)
                    hc=is_hungarian_case(j)
                    pc=is_pascal_case(j)
                    #ec=spellcheck(j)

                    if(variable_list.index(i)==0):
                        result+="variables with name --->"+"'"+cc+"'"+"\n"
                        result+="Variables with name--->"+"'"+hc+"'"+"\n"
                        result+="Variables with name--->"+"'"+pc+"'"+"\n"
                        #result["variables"].append(ec)
                    if(variable_list.index(i)==1):
                        result+="Functions with name--->"+"'"+cc+"'"+"\n"
                        result+="Functions with name--->"+"'"+hc+"'"+"\n"
                        result+="Functions with name--->"+"'"+pc+"'"+"\n"
                        #result["functions"].append(ec)
                    if(variable_list.index(i)==2):
                        result+="Parameters with name--->"+"'"+cc+"'"+"\n"
                        result+="Parameters with name-->"+"'"+hc+"'"+"\n"
                        result+="Parameters with name-->"+"'"+pc+"'"+"\n"
                        #result["parameters"].append(ec)
                    if(variable_list.index(i)==3):
                        result+="Classnames with name--->"+"'"+cc+"'"+"\n"
                        result+="Classnames with name--->"+"'"+hc+"'"+"\n"
                        result+="Classnames with name--->"+"'"+pc+"'"+"\n"
                        #result["classnames"].append(ec)
    return result

                    
def code_metrics(file_content,funclines,linelength,filelength):
    ll=line_length_details(file_content,int(linelength))
    fl=func_length_details(file_content,int(funclines))
    filel=file_length_details(file_content,int(filelength))
    return '\n'.join(['Line Length details \n'+ll+'\n\n','Function Length details\n'+fl+"\n\n",'File length details\n'+filel+'\n\n'])

    


##Comment Ratio Target
def comment_ratio_target(filetext):
    a=list(filetext.split("\n"))
    total_length=len(a)
    print(total_length)
    comment_length=0
    empty_lines=0
    for i in a:    
        if(i.strip(' ').startswith("#")):        
            comment_length+=1
        elif(i.strip(' ').startswith(("'''", '"""'))):    
               
            comment_length+=1    
        if(len(i.strip(" "))==0):        
            empty_lines+=1
    
    total_length=total_length-empty_lines
    
    if(total_length>0):    
        result=(comment_length/total_length)*100
        return result
    else:
        return 0
    


def func(p):    
    comment_length=0    
    for i in p:        
        if(i.strip(' ').startswith("#")):            
            comment_length+=1   
        elif(i.strip(' ').startswith(("'''", '"""'))):     
                  
            comment_length+=1    
    return comment_length

def comment_density(file_text):
    a=list(file_text.split("\n"))
    com_len=[]
    count=0
    for i in range(len(a)):
        if(a[i].strip(' ').startswith("#") or a[i].strip(" ").startswith("'''")):
        
            com_len.append(i-count)
            count=i
    if(len(com_len)>0):
        return math.ceil(sum(com_len)/len(com_len))
    else:
        return 0



##Comment Density
def comment_density_deprec(filetext,comment_density):
    
    b=100//comment_density
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
        print("Code Density is not satisfied")
    else:    
        print("Code Density is Satisfied")