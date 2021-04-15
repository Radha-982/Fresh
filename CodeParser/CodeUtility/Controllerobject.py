from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, BlobProperties
from azure.storage.blob import BlobClient
import azure.functions as func
import os
import uuid
from .Codestyle import CodeOptions


class ControllerObject:
    def process_file(self,file_content,options,extension):                
        return_msg=codestyleObj.style(file_content,options,extension)     
        return return_msg
    def access_repo(self, path, in_type,blobname):                       
        container_name = factory.down_repo(path,in_type,blobname)        
        print(container_name)        
        return container_name
    def return_repo(self,container_name,out_type):        
        msg=uploadobj.upload_repo(container_name,out_type)        
        return msg


class Codestyle:
    def style(self,file_content,options,extension):        
               
        file_text=''        
        file_validation="" 
        comment_count=0
        func_header_count=0       
        for opt in options:            
            if(opt=="validate"):                
                file_validation=self.validate(file_content,extension)            
            elif(opt=="format"):                
                file_text=self.format(file_content,extension)               
                file_content=file_text            
            elif(opt=="comment" and extension=="python"):
                                                
                file_text,comment_count,func_header_count=self.comment(file_content,extension)
                #print(file_text)
                file_content=file_text        
        return {"result":file_text,"validations":file_validation,'Functionheadercount':func_header_count,'commentcount':comment_count}        
    def validate(self,file_content,extension):        
        codeobject=CodeOptions()        
        result=codeobject.validate_code(file_content,extension)        
        return result
    def format(self,file_content,extension):        
        codeobject=CodeOptions()        
        result=codeobject.format_code(file_content,extension)        
        return result            
    def comment(self,file_content,extension):        
        codeobject=CodeOptions()        
        result=codeobject.comment_code(file_content,extension)        
        return result
codestyleObj=Codestyle()    
class Repo:
    def down_repo(self, path,in_type,blobname): 
                      
        if(in_type=="Git"):            
            container_name=self.gget_repo(path)        
        elif(in_type=='Azure Blob'):
                       
            container_name=self.get_blob(path,blobname)        
        elif(in_type=="zip"):               
            container_name=self.get_zip(path)        
        elif(in_type=="file"):            
            container_name=self.get_file(path)        
            print(container_name)        
        return container_name    
    def gget_repo(self,path):                
        '''print("Downloading Git repo")        
        g=Github(verify=False)       
        user = g.get_user("Radha-982")        
        repo=g.get_repo(path) '''
        import subprocess
        from subprocess import Popen,PIPE
        import os
        os.chdir("F:/GIT")
        s=Popen("git clone "+path,shell=True,stdout=subprocess.PIPE)
        import time
        time.sleep(7)
        a=path.split("/")[-1].replace(".git","")

               
        return a            
        #connection_string="DefaultEndpointsProtocol=https;AccountName=parserrepos;AccountKey=tJMwHAPSWGP4zoJDjLo3W7S9oRVbCiGYKGA15x26lOHALy3gHWtu/9PBmzVnti//Ykwb4sP4YPUG+JgWlIc8Ig==;EndpointSuffix=core.windows.net"        blob_service_client1 = BlobServiceClient.from_connection_string(connection_string)        uid = uuid.uuid1().fields[0]                blobname="rk-staging"+repo.name.lower()+str(uid)                container_client = blob_service_client1.get_container_client(blobname)        container_client.create_container()        for i in r:            blob_client = container_client.get_blob_client(i.path)            blob_client.upload_blob(i.decoded_content,blob_type="BlockBlob")

        #return blobname      
    def get_blob(self,path,blobname):
        #blob details
        conn_str = path
        bname=blobname
        os.chdir('F:\GIT')
        os.mkdir(blobname)
        os.chdir('F:\GIT\\'+blobname)
        li=path.split(';')
        


        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        configObject = blob_service_client.get_container_client(bname).list_blobs()
        for config in configObject:
            if "/" in "{}".format(config.name):
                print("there is a path in this")
                #extract the folder path and check if that folder exists locally, and if not create it
                head, tail = os.path.split("{}".format(config.name))
                 
                if (os.path.isdir(os.getcwd()+ "/" + head)):
                    configObject.get_blob_to_path(blobname,config.name,os.getcwd()+ "/" + head + "/" + tail)
                else:
                    #create the diretcory and download the file to it
                    
                    os.makedirs(os.getcwd()+ "/" + head, exist_ok=True)
                    configObject.get_blob_to_path(blobname,config.name,os.getcwd()+ "/" + head + "/" + tail)
            else:
                configObject.get_blob_to_path(blobname,config.name,config.name)
            
        return blobname
    def get_zip(self,path):
        print("Downloading zip")
        return ""    
    def get_file(self,path):
        print("Downloading file")        
        return ""    

factory = Repo()
class UploadRepo:    
    def upload_repo(self, container_name,out_type):        
        msg=''        
        if(out_type=="git"):            
            msg=self.convert_to_git(container_name)        
        elif(out_type=="blob"):            
            msg=self.convert_to_blob(container_name)        
        elif(out_type=="zip"):            
            msg=self.convert_to_zip(container_name)        
        elif(out_type=="file"):            
            msg=self.convert_to_file(container_name)        
        return msg
    def convert_to_git(self,container_name):
        print("Converting to git")        
        return None
    def convert_to_blob(self,container_name):
        print("Converting to blob")        
        return None
    def convert_to_zip(self,container_name):
        print("Converting to zip")        
        return None
    def convert_to_file(self,container_name):
        print("Converting to file")        
        return None
uploadobj=UploadRepo()    