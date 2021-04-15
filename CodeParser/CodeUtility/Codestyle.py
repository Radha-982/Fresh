import nbformat
from nbformat import v4 as nbf
from yapf.yapflib.yapf_api import FormatFile,FormatCode
#import pycodestyle
from bs4 import BeautifulSoup
import ast
import os
import json
class CodeOptions:    
    a=''  
    comment_count=0
    func_header_count=0  
    def format_code(self,file_content,extension):           
        if(extension=="python"):
            #print(file_content)            
            #file_content=file_content.decode("utf-8")                        
            result=FormatCode(file_content)            
            #print("Formated code",result)            
            #print(result)            
            return result[0]                
        elif(extension=='notebook'):            
            nb=file_content            
            #nb=nbformat.read(inputnb,4)            
            newnb = nbf.new_notebook()            
            newcells = []                                    
            for idx, cell in enumerate(nb["cells"]):                   
                if cell["cell_type"]=='code':                    
                    try:                        
                        formatted=FormatCode(cell["source"])                        
                        #print(formatted)                        
                        newcell = nbf.new_code_cell(formatted)                        
                        #print(newcell)                        
                        newcells.append(newcell)                        
                    except:                        
                        formatted=cell["source"]                        
                        newcell = nbf.new_code_cell(formatted)                        
                        newcells.append(newcell)                
                else:                    
                    formatted=cell["source"]                    
                    newcell = nbf.new_markdown_cell(formatted)                    
                    newcells.append(newcell)                
                    #print(newcells)                            
                    newnb = nbf.new_notebook(cells=newcells)                    
        elif(extension=="HTML"):            
            #file_content=file_content.decode("utf-8")            
            soup=BeautifulSoup(file_content,"html.parser")            
            result=soup.prettify().encode('cp1252', errors='ignore')            
            a=result.decode('utf-8')            
            return a


    def validate_code(self,file_content,extension): 
        #print(file_content)       
        if(extension=="python"):            
            #print("validate",file_content)            
            #file_content=file_content.decode("utf-8")
                      
            root = ast.parse(str(file_content))           
            #print(ast.dump(root))            
            variables = sorted({node.id for node in ast.walk(root) if isinstance(node, ast.Name) and not isinstance(node.ctx,ast.Load)})            
            functions=sorted({node.name for node in ast.walk(root) if isinstance(node, ast.FunctionDef)})            
            parameters=sorted({ arg.arg for node in ast.walk(root) if isinstance(node, ast.FunctionDef) for arg in node.args.args})            
            classes=sorted({ node.name for node in ast.walk(root) if isinstance(node, ast.ClassDef)})            
            #print('Variables:' ,variables)            #print('Functions:' ,functions)            
            #print('Parameters:', parameters)            
            #print('Classes:' ,classes)            
            varList=[variables,functions,parameters,classes]            
            #print(varList)            
            return varList    
                    

        elif(extension=="HTML"):            
            from io import StringIO            
            #print("RADHA",file_content)            
            #file_content=file_content.decode("utf-8")            
            r=file_content
            #print(file_content)            
            '''soup=BeautifulSoup(r)            
            form = soup.find('form')            
            inputs = form.find_all('input')            
            variables=[]            
            for i in inputs:                
                variables.append(i.get('name'))            
                #print(variables)
            return variables'''


    
    def comment_code(self,file_content,extension):        
        
                
        if(extension=='python'):      
                  
            p = ast.parse(str(file_content))             
            CodeOptions.a=str(file_content).splitlines()            
            v = AnalysisNodeVisitor()            
            v.visit(p)            
                        
            return "\n".join(CodeOptions.a),CodeOptions.comment_count,CodeOptions.func_header_count                
object1=CodeOptions()
def getcomment(block):    
    dirname = os.path.dirname(__file__)    
    with open(os.path.join(dirname, 'comment_statements.json'), 'r') as infile:        
        json_object = json.load(infile) 
        #print(json_object[block]["Template-1"])               
        return (json_object[block]["Template-1"])
class AnalysisNodeVisitor(ast.NodeVisitor):    
    def visit_Import(self,node):        
        CodeOptions.a[node.lineno-1]="#"+getcomment("Imports")+"\n"+CodeOptions.a[node.lineno-1]        
        CodeOptions.comment_count+=1          
        ast.NodeVisitor.generic_visit(self, node)
    def visit_ImportFrom(self,node):        
        ast.NodeVisitor.generic_visit(self, node)
    def visit_Call(self,node):        
        if(isinstance(node.func,ast.Name)):            
            com=getcomment("Calls/Triggers").replace('###function###' ,node.func.id)            
            CodeOptions.a[node.lineno-1]="#"+com+"\n"+CodeOptions.a[node.lineno-1]
            CodeOptions.comment_count+=1        
            ast.NodeVisitor.generic_visit(self,node)

    def visit_FunctionDef(self,node):        
        com=getcomment("Functions").replace("######",node.name)        
        CodeOptions.a[node.lineno-1]="#"+com+"\n"+CodeOptions.a[node.lineno-1]          
        CodeOptions.comment_count+=1
        CodeOptions.func_header_count+=1         
        ast.NodeVisitor.generic_visit(self,node)    
    def visit_Assign(self,node):        
                        
        variable_name=''        
        if(isinstance(node.targets[0],ast.Name)):            
            variable_name=node.targets[0].id        
        elif(isinstance(node.targets[0],ast.Attribute)):            
            variable_name=node.targets[0].attr                    
            com=getcomment("Declaration").replace("###variables###",variable_name)        
            CodeOptions.a[node.lineno-1]="#"+com+"\n"+CodeOptions.a[node.lineno-1]
            CodeOptions.comment_count+=1          
            ast.NodeVisitor.generic_visit(self, node)     
    def visit_BinOp(self, node):        
        #print('Node type: BinOp and fields: ', node._fields)        
        ast.NodeVisitor.generic_visit(self, node)
    def visit_Expr(self, node):        
        #print('Node type: Expr and fields: ', node._fields)        
        ast.NodeVisitor.generic_visit(self, node)   

    def visit_Name(self,node):        
        ast.NodeVisitor.generic_visit(self, node)    
    def visit_For(self,node):        
        iteration_variable=''        
        if(isinstance(node.iter,ast.Name)):            
            iteration_variable=node.iter.id        
        else:            
            iteration_variable="iterator"                
            com=getcomment("For Loop").replace("###iterator###",iteration_variable)        
            CodeOptions.a[node.lineno-1]="#"+com+"\n"+CodeOptions.a[node.lineno-1]
            CodeOptions.comment_count+=1          
            ast.NodeVisitor.generic_visit(self, node)    
    def visit_While(self,node):        
        com=getcomment("While")        
        CodeOptions.a[node.lineno-1]="#"+com+"\n"+CodeOptions.a[node.lineno-1]
        CodeOptions.comment_count+=1                  
        ast.NodeVisitor.generic_visit(self, node)              
    def visit_If(self,node):        
        com=getcomment("If")        
        CodeOptions.a[node.lineno-1]="#"+com+"\n"+CodeOptions.a[node.lineno-1]
        CodeOptions.comment_count+=1          
        #print("If ",ast.dump(node.test))        
        ast.NodeVisitor.generic_visit(self, node)    
    def visit_ClassDef(self,node):        
        #print("class ",node.name)        
        com=getcomment("Classes").replace("####",node.name)        
        CodeOptions.a[node.lineno-1]="#"+com+"\n"+CodeOptions.a[node.lineno-1]
        CodeOptions.comment_count+=1          
        ast.NodeVisitor.generic_visit(self, node)    
    def visit_Try(self,node):        
        com=getcomment("Try")        
        CodeOptions.a[node.lineno-1]="#"+com+"\n"+CodeOptions.a[node.lineno-1]
        CodeOptions.comment_count+=1                  
        ast.NodeVisitor.generic_visit(self, node)