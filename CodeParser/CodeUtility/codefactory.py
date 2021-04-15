from .Controllerobject import ControllerObject
import urllib.parse as u
import nbformat
from googleapiclient.discovery import build
from google.oauth2 import service_account
from azure.storage.blob  import BlobServiceClient, BlobClient, ContainerClient, BlobProperties
from azure.storage.blob import BlobClient
import azure.functions as func
from yapf.yapflib.yapf_api import FormatFile, FormatCode
import subprocess
from subprocess import Popen,PIPE
import json
import os
from pathlib import Path
from git import Repo, RemoteReference
from . import Sheet
import pandas as pd
import datetime
from . import Metrics
from oauth2client.service_account import ServiceAccountCredentials
import uuid
class Controller:

    def __init__(self, path,user_name,in_type,password,blobname):
        print("Intialising the details")                
                
                        
        self.path=path        
        self.in_type=in_type        
        self.user_name=user_name
        self.password=password
        self.blobname=blobname


    def process(self):                
        co_obj=ControllerObject()        
        #Access the repo        
        container_name=co_obj.access_repo(self.path,self.in_type,self.blobname)        
        self.parse_files(container_name)        
        out_type=''        
        self.return_folder(container_name,out_type)


    def parse_files(self, container_name):
    
        
        co_obj = ControllerObject()

        #change the directory according to your system  
        PATH="F:/GIT/"+str(container_name)
        os.chdir("F:/GIT/"+str(container_name))

        #Access the file info entered by user
        scope = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.metadata','https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('F:/GIT/CodeParser/Keys.json', scope)
        data=Sheet.read_spreadsheet_to_df(credentials,"11Gmnw1DZj9tXLU4ogQ0oOHMA5tomMpvF97pqxpKD4oI","Folder and Files Config")

        #output data to be written
        write_data={'ConnectionFriendlyName':[],"FolderName":[],	"FileName":[],	"Subfolder":[],	"Exclude Pattern":[],	"AlertEmail":[],	"AutoComment":[],	"AutoComment-Result":[]	,"Validate":[],	"Validate-Result":[],	"Format":[],	"Format-Result":[],	"Comment Ratio Target":[]	,"Comment Ratio Target Result":[],	"Comment Density":[],	"Comment Density Result":[],	"Validate-PercentTarget":[],	"Validate-Percent Target Result":[],	"Validate-Linelength":[],	"Validate-Linelength Result":[],	"Validate-FunctionLength":[],	"Validate-FunctionLength Result":[],	"Validate-File Length":[],	"Validate-File Length-Result":[]}
        options=[]
        write_datadetails={'ConnectionFriendlyName':[],	'FolderName':[],	'FileName':[],	'Type':[],	'DateStamp':[],	'Issue':[]	,'Assigned To':[],	'Resolved On':[]}
        notes=[]
        for i in data.to_dict(orient="records"):
            options=[]
            if(i["AutoComment"]=="Yes"):
                options.append("comment")
            if(i["Format"]=="Yes"):
                options.append("format")
            if(i["Validate"]=="Yes"):
                options.append("validate")
            if(i["ConnectionFriendlyName"]==container_name):
                if(i["FolderName"]!='/'):
                    PATH="F:/GIT/"+str(container_name)+"/"+str(i["FolderName"])
                    os.chdir(PATH)
                    for path, dirs, files in os.walk(PATH):
                        for filename in files:
                            noteslist=[]
                            fullpath = os.path.join(path, filename)
                            if(i['FileName']=="*.*"):
                                if(fullpath.endswith(".py")):
                                    with open(fullpath, 'r+') as f:
                                        data =f.read()
                                
                                        extension="python"
                                        msg=co_obj.process_file(data,options,extension)
                                        file_con=msg["result"]
                                        f.seek(0)
                                        f.truncate()

                                        write_data=self.write_to(write_data,filename,i,file_con)
                                        noteslist.append('Auto Commenting\n'+self.comment_details(file_con) +'\n\nVariable Metrics\n'+ Metrics.varaible_metrics(msg['validations'])+'\n\n Code Metrics\n'+Metrics.code_metrics(file_con,i['Validate-FunctionLength'],i['Validate-Linelength'],i['Validate-File Length'])  )                                        
                                        


                                        write_datadetails=self.write_todetails(write_datadetails,filename,i,file_con,msg['validations'])
                                        f.write(msg["result"])
                                        f.close()

                            
                                elif(fullpath.endswith(".html")):
                                    with open(fullpath, 'r+') as f:
                                        data =f.read()
                                        extension="HTML"
                                        msg=co_obj.process_file(data,options,extension)
                                        f.seek(0)
                                        f.truncate()
                                        
                                        f.write(msg["result"])
                                        f.close()
                            else:
                                files_extensions=list(i["FileName"].split(","))
                                
                                extension_file='.py'
                                if(filename.endswith(".py")):
                                    extension_file=".py"
                                if(extension_file in files_extensions):
                                    if(fullpath.endswith(".py")):
                                        with open(fullpath, 'r+') as f:
                                            data =f.read()
                                    
                                            extension="python"
                                            msg=co_obj.process_file(data,options,extension)
                                            file_con=msg["result"]
                                            f.seek(0)
                                            f.truncate()
                                            
                                            write_data=self.write_to(write_data,filename,i,file_con)
                                            noteslist.append('Auto Commenting\n'+self.comment_details(file_con) +'\n\nVariable Metrics\n'+ Metrics.varaible_metrics(msg['validations'])+'\n\n Code Metrics\n'+Metrics.code_metrics(file_con,i['Validate-FunctionLength'],i['Validate-Linelength'],i['Validate-File Length'])  )                                        
                                            write_datadetails=self.write_todetails(write_datadetails,filename,i,file_con,msg['validations'])

                                            f.write(msg["result"])
                                            f.close()

                            
                                    elif(fullpath.endswith(".html")):
                                        with open(fullpath, 'r+') as f:
                                            data =f.read()
                                            extension="HTML"
                                            msg=co_obj.process_file(data,options,extension)
                                            f.seek(0)
                                            f.truncate()
                                            
                                            f.write(msg["result"])
                                            f.close()
                            notes.append(noteslist)


                elif(i["FolderName"] is "/"):
                    PATH="F:/GIT/"+str(container_name)
                    os.chdir(PATH)
                    
                    for path, dirs, files in os.walk(PATH):
                        
                        for filename in files:
                            noteslist=[]
                            fullpath = os.path.join(path, filename)
                            if(i['FileName']=="*.*"):
                                if(fullpath.endswith(".py")):
                                    with open(fullpath, 'r+') as f:
                                        data =f.read()
                                        extension="python"
                                        msg=co_obj.process_file(data,options,extension)
                                        
                                        file_con=msg["result"]
                                        f.seek(0)
                                        f.truncate()
                                        f.write(msg["result"])
                                        write_data=self.write_to(write_data,filename,i,file_con)
                                        noteslist.append('Auto Commenting\n'+self.comment_details(file_con) +'\n\nVariable Metrics\n'+ Metrics.varaible_metrics(msg['validations'])+'\n\n Code Metrics\n'+Metrics.code_metrics(file_con,i['Validate-FunctionLength'],i['Validate-Linelength'],i['Validate-File Length'])  )                                        
                                        write_datadetails=self.write_todetails(write_datadetails,filename,i,file_con,msg['validations'])

                                        f.close()

                            
                                elif(fullpath.endswith(".html")):
                                    with open(fullpath, 'r+') as f:
                                        data =f.read()
                                        extension="HTML"
                                        msg=co_obj.process_file(data,options,extension)
                                        f.seek(0)
                                        f.truncate()
                                        
                                        f.write(msg["result"])
                                        f.close()
                            else:
                                files_extensions=list(i["FileName"].split(","))
                                extension_file='.py'
                                
                                if(filename.endswith(".py")):
                                    extension_file="*.py"
                                if(extension_file in files_extensions):
                                    
                                    if(fullpath.endswith(".py")):
                                        with open(fullpath, 'r+') as f:
                                            data =f.read()
                                
                                            extension="python"
                                            msg=co_obj.process_file(data,options,extension)
                                            #print(msg["result"])
                                            file_con=msg["result"]
                                            f.seek(0)
                                            write_data=self.write_to(write_data,filename,i,file_con)
                                            noteslist.append('Auto Commenting\n'+self.comment_details(file_con) +'\n\nVariable Metrics\n'+ Metrics.varaible_metrics(msg['validations'])+'\n\n Code Metrics\n'+Metrics.code_metrics(file_con,i['Validate-FunctionLength'],i['Validate-Linelength'],i['Validate-File Length'])  )                                        
                                            write_datadetails=self.write_todetails(write_datadetails,filename,i,file_con,msg['validations'])

                                            f.truncate()
                                            f.write(msg["result"])
                                            f.close()

                            
                                    elif(fullpath.endswith(".html")):
                                        with open(fullpath, 'r+') as f:
                                            data =f.read()
                                            extension="HTML"
                                            msg=co_obj.process_file(data,options,extension)
                                            f.seek(0)
                                            f.truncate()
                                            print(msg["validations"])
                                            f.write(msg["result"])
                                            f.close()
                            if(len(noteslist)>0):
                                notes.append(noteslist)
    

        data_frame=pd.DataFrame(write_data)
        print(write_datadetails)
        print(len(notes))
        range= {'sheetId':1311439114,
        'startRowIndex':1,
        'endRowIndex':10,'startColumnIndex':3,
        'endColumnIndex':4

        }
        re=Sheet.add_notes(credentials,'1ow_zDxLcOYCWcPUguzp4pTgGmxxSXsABu5aMbF5RFYA',notes,range)
        
        '''id = uuid.uuid1().fields[0]     
        file_id=Sheet.copy_spreadsheet(credentials,"11Gmnw1DZj9tXLU4ogQ0oOHMA5tomMpvF97pqxpKD4oI","LeadMotors-CodeIndex-Run"+str(id),"16xZChX43rZPlvZ6P4fh56hQQOMq6RH2X")
        print(file_id)

        request=Sheet.write_df_to_spreadsheet(credentials,file_id,"CodeIndex Results",data_frame)
        print(request)'''

        '''dataf={"FileID":"","ConnectionID":'',"Active":'','FolderName':'',"FileName":'',"AlertEmail":"rk@gmail.com","AlertCCEmail":"rk@gmail.com","CommentSuccess":"","ValidateSuccess":'',"FormatSuccess":'',"CodeMetrics":'',"VariableStats":""}
        data_frame=[]
        for path, dirs, files in os.walk(PATH):
            for filename in files:
                fullpath = os.path.join(path, filename)
                
                if(fullpath.endswith(".py")):
                    with open(fullpath, 'r+') as f:
                        data =f.read()
                        
                        extension="python"
                        msg=co_obj.process_file(data,self.options,extension)
                        #print(msg["result"])
                        f.seek(0)
                        f.truncate()
                        f.write(msg["result"])
                        dataf["FileName"]=path
                        dataf["CommentSuccess"]="YES"
                        dataf["ValidateSuccess"]="YES"
                        dataf["FormatSuccess"]="YES"

                        dataf['VariableStats']=Metrics.varaible_metrics(msg["validations"])
                        dataf["CodeMetrics"]=Metrics.code_metrics(msg["result"],7)
                        data_frame.append(dataf)
                        f.close()

                    
                elif(fullpath.endswith(".html")):
                    with open(fullpath, 'r+') as f:
                        data =f.read()
                        extension="HTML"
                        msg=co_obj.process_file(data,self.options,extension)
                        f.seek(0)
                        f.truncate()
                        print(msg["validations"])
                        f.write(msg["result"])
                        f.close()

        '''    
        
        
        '''id = uuid.uuid1().fields[0]
        print(Popen("git checkout -b "+"Commented"+str(id),shell=True,stdout=subprocess.PIPE).communicate())
        print(Popen("git add --a",shell=True,stdout=subprocess.PIPE).communicate())
        print(Popen('git commit -m "Code comments done"',shell=True,stdout=subprocess.PIPE).communicate())
        print(Popen("git push -u origin "+"Commented"+str(id),shell=True,stdout=subprocess.PIPE).communicate())

        git_stat={"ConnectionFriendlyName":[],"AlertEmail":[],"Sync Status":[],"Sync error":[]}
        git_stat["ConnectionFriendlyName"].append(container_name)
        git_stat["AlertEmail"].append("Ajay.Gangula@gmail.com")
        git_stat["Sync Status"].append("Push Success with branch"+"Commented"+str(id))
        git_stat["Sync error"].append(None)
        df=pd.DataFrame(git_stat)
        request=Sheet.write_df_to_spreadsheet(credentials,file_id,"CodeIndex -Sync Results",df) 
        print(request)'''

        #print(Popen("git status",shell=True,stdout=subprocess.PIPE).communicate())            


                


                      
        '''g=Github("7457bdef77c93e05b9eec147009644d533ba0efe",verify=False)        
        repo=g.get_repo("Radha-982/temp")                        
        while contents:            
            file_content = contents.pop(0)            
            if file_content.type == "dir":                
                contents.extend(repo.get_contents(file_content.path))            
            else:                
                file_text=file_content.decoded_content                
                msg=''                
                if(file_content.path.endswith(".py")):                    
                    extension="python"                      
                    filename=file_content.path                    
                    msg=co_obj.process_file(file_text,self.options,extension)                                        
                    update_file=repo.get_contents(filename,ref="Sansad")                    
                    repo.delete_file(update_file.path, "removing file", update_file.sha, branch="Sansad")                    
                    repo.create_file(update_file.path, "Updated", str(msg["result"]), branch="Sansad")
                    co_obj = ControllerObject()         
                    print(container_name)        
                    contents = container_name.get_contents("")
                elif(file_content.path.endswith(".html")):
                    extension = "HTML"                    
                    msg = co_obj.process_file(file_text, self.options, extension)'''                                                    
                                                
                   
    def write_to(self,write_data,filename,i,file_con):
        write_data["ConnectionFriendlyName"].append(i["ConnectionFriendlyName"])
        write_data["FolderName"].append(i["FolderName"])
        write_data["FileName"].append(filename)
        write_data["Subfolder"].append(i["Subfolder"])
        write_data["Exclude Pattern"].append(i["Exclude Pattern"])
        write_data["AlertEmail"].append(i["AlertEmail"])
        write_data["AutoComment"].append(i["AutoComment"])
        write_data["AutoComment-Result"].append(i["AutoComment"])
        write_data["Validate"].append(i["Validate"])
        write_data["Validate-Result"].append(i["Validate"])
        write_data["Format"].append(i["Format"])
        write_data["Format-Result"].append("Yes")
        write_data["Comment Ratio Target"].append(i["Comment Ratio Target"])
        write_data["Comment Ratio Target Result"].append(Metrics.comment_ratio_target(file_con))
        write_data["Comment Density"].append(i["Comment Density"])
        write_data["Comment Density Result"].append(Metrics.comment_density(file_con))
        write_data["Validate-PercentTarget"].append(None)
        write_data["Validate-Percent Target Result"].append(None)

        write_data["Validate-Linelength"].append(i["Validate-Linelength"])
        write_data["Validate-Linelength Result"].append(Metrics.line_length(file_con))
        write_data["Validate-FunctionLength"].append(i["Validate-FunctionLength"])
        write_data["Validate-FunctionLength Result"].append(Metrics.func_length(file_con))
        write_data["Validate-File Length"].append(i["Validate-File Length"])
        write_data["Validate-File Length-Result"].append(Metrics.file_length(file_con))
        return write_data
    def comment_details(self, filetext):
        a=filetext.split('\n')
        commentlines=[]
        for i in a:
            if(i.strip('').startswith('###')):
                commentlines.append(str(a.index(i)))
        return "Commentlines are inserted at lines  ---"+','.join(commentlines)



    def write_todetails(self,write_datadetails,filename,i,file_con,validations):
        write_datadetails['ConnectionFriendlyName'].append(i["ConnectionFriendlyName"])
        write_datadetails["FolderName"].append(i["FolderName"])
        write_datadetails["FileName"].append(filename)

        write_datadetails['Type'].append('hi')
        write_datadetails["DateStamp"].append(datetime.datetime.now())
        write_datadetails['Issue'].append(None)
        write_datadetails['Assigned To'].append('123452@gmail.com')
        write_datadetails['Resolved On'].append(None)
        


        return write_datadetails

                       

    def return_folder(self, container_name, out_type):
        co_obj = ControllerObject()        
        msg = co_obj.return_repo(container_name, out_type)