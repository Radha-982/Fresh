import logging
import gspread
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
import azure.functions as func
from .codefactory import Controller
import urllib.parse as u
from googleapiclient.http import MediaFileUpload
import datetime
from . import Sheet
from . import credentials
from oauth2client.service_account import ServiceAccountCredentials

def main(req: func.HttpRequest) -> func.HttpResponse:    
    logging.info('Python HTTP trigger function processed a request.')
        
     
    scope = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.metadata','https://spreadsheets.google.com/feeds']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('F:\GIT\CodeParser\Keys.json', scope)
    '''data=Sheet.read_spreadsheet_to_df(credentials,"11Gmnw1DZj9tXLU4ogQ0oOHMA5tomMpvF97pqxpKD4oI","CentralConnections!A1:R3")
    print(data)'''


    re=Sheet.get_central_credentails_file_id(credentials,"11Gmnw1DZj9tXLU4ogQ0oOHMA5tomMpvF97pqxpKD4oI")
    resource_dict=Sheet.read_credentials_to_dict(credentials,re,"Sheet1")
    data=resource_dict["leadmotors"]

    

    path=''
    in_type = data['type']  
    if(in_type=='Git'):

        path = data['RepositoryURL']
        user_name=data['UserName']   
        
        password=data['Password']
        container_name=''
        objcontroller=Controller(path,user_name,in_type,password,container_name)
    else:
        password=data['AccountKey']
        path=data['ConnectionString']
        container_name=data['ContainerName']
        user_name=data['AccountName']  
        objcontroller=Controller(path,user_name,in_type,password,container_name)     


    
    #creating an instance with intialising with values    
    
    objcontroller.process()
    
    if path:        
        return func.HttpResponse(f"Hello, {path}. This HTTP triggered function executed successfully.")    
    else:        
        return func.HttpResponse("This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",             status_code=200        )
