import os, logging, re
import json
from io import StringIO
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from apiclient.http import MediaFileUpload

import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_file_parents_id(credentials, file_id):
    drive_api = build('drive', 'v3', credentials = credentials)
    result = drive_api.files().get(fileId=file_id, fields= "parents").execute()
    return result['parents'][0] 
def get_file_name(credentials, file_id):
    drive_api = build('drive', 'v3', credentials = credentials)
    result = drive_api.files().get(fileId=file_id, fields= "name").execute()
    return result['name']
def get_file_id_for_master_file(credentials, master_file_id, file_name):
    drive_api = build('drive', 'v3', credentials = credentials)


    result = drive_api.files().get(fileId=master_file_id, fields= "parents").execute()
    parents_id = result['parents'][0] 
    query = f"name contains '{file_name}' and '{parents_id}' in parents"
    page_token = None
    result = drive_api.files().list( q = query,
                                     fields="nextPageToken, files(id, name, mimeType)",
                                     pageToken=page_token ).execute()
    return result["files"][0]['id']


def get_central_credentails_file_id(credentials, file_id):
    drive_api = build('drive', 'v3', credentials = credentials)
    
    result = drive_api.files().get(fileId=file_id, fields= "parents").execute()
    version_folder_id = result['parents'][0] 
    result = drive_api.files().get(fileId=version_folder_id, fields= "parents").execute()
    db_folder_id = result['parents'][0] 
    result = drive_api.files().get(fileId=db_folder_id, fields= "parents").execute()
    module_folder_id = result['parents'][0] 
    result = drive_api.files().get(fileId=module_folder_id, fields= "parents").execute()
    unify_folder_id = result['parents'][0]
    
    query = f"name contains '_Platform' and '{unify_folder_id}' in parents"
    result = drive_api.files().list( q = query,
                                     fields="nextPageToken, files(id, name, mimeType)").execute()
    platform_folder_id = result["files"][0]['id']
    
    query = f"name contains 'CentralCredentials' and '{platform_folder_id}' in parents"
    result = drive_api.files().list( q = query,
                                     fields="nextPageToken, files(id, name, mimeType)").execute()
    return result["files"][0]['id']



def read_credentials_to_dict(credentials, spreadsheet_id, range_):

    service = build('sheets', 'v4', credentials=credentials)
    result  = service.spreadsheets().values().get(spreadsheetId= spreadsheet_id, range= range_).execute()
    values = result.get('values', [])
    values.pop(0)
    values.pop(0)
    credentials_dict = {}

    for i in range(len(values)):
        if values[i][0] != '':
            cred = {}
            credentials_dict[values[i][0]] = cred
            cred["type"] = values[i][1]
            if len(values[i]) > 3:
                cred[values[i][2]] = values[i][3]
            else:
                cred[values[i][2]] = ""

        else:
            if len(values[i]) > 3:
                cred[values[i][2]] = values[i][3]
            else:
                cred[values[i][2]] = ""
    return credentials_dict


#Parameters -> List of Scopes 
def get_credentials(scopes: list)-> ServiceAccountCredentials:
    credentials = ServiceAccountCredentials.from_json_keyfile_name('Keys.json', scopes)
    return credentials

#Parameters -> credentials, spreadsheet_id, range_(A1 Notation), df
def write_df_to_spreadsheet(credentials, spreadsheet_id, range_, df):
    
    service = build('sheets', 'v4', credentials=credentials)
    values = [df.columns.values.tolist()]
    values.extend(df.values.tolist())
    data = [{'range' : range_, 'values' : values }]
    
    batch_update_values_request_body = {
        'value_input_option': 'RAW',
        'data': data }

    request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                          body=batch_update_values_request_body).execute()
    return request
    
#Parameters -> credentials
def get_sheet_id(credentials, spreadsheet_id, sheet_name):
    service = build('sheets', 'v4', credentials=credentials)
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', [])
    for i in range(len(sheets)):
        title = sheets[i].get("properties").get("title")
        if title.strip().lower() == sheet_name.strip().lower():
            return sheets[i].get("properties").get("sheetId")
    return None

#Parameters -> credentials
def copy_spreadsheet(credentials, file_id, name = None, parent_folder = None, copy_permissions = True):
    service = build('drive', 'v3', credentials=credentials)
    body = {}
    if name:
        body["name"] = name
    if parent_folder:
        body["parents"] = [parent_folder]
    file = service.files().copy(fileId = file_id, body=body, fields='id, name, parents').execute()
    
    if not copy_permissions:
        return file['id']
    
    response = service.files().get(fileId = file_id , fields = "parents,permissions").execute()
    
    for perm in response['permissions']:
        print(perm)
        new_permission = {
          'emailAddress': perm['emailAddress'],
          'type': perm['type'],
          'role': perm['role']
          }
        if perm['role'] == "owner":
            new_permission['role'] = 'writer'
        service.permissions().create(fileId=file['id'], body=new_permission).execute()
    
    return file['id']

#Parameters -> credentials
def read_spreadsheet_to_df(credentials, spreadsheet_id, range_):
    # Call the Sheets API
    service = build('sheets', 'v4', credentials=credentials)
    result  = service.spreadsheets().values().get(spreadsheetId= spreadsheet_id, range= range_).execute()
    values = result.get('values', [])
    if not values:
        return None
    else:
        values.pop(0) # Instructions row
        df = pd.DataFrame(values)
        df.columns = df.iloc[0]
        df.drop(df.index[0], inplace=True)
        return df

#Parameters -> credentials, spreadsheet_id, list of note range_(A1 Notation)
def add_notes(credentials, spreadsheet_id, note_list, range_):
    service = build('sheets', 'v4', credentials=credentials)
    rows = []
    for notes in note_list:
        values = []
        for note in notes:
            values.append({"note":note})
        rows.append({"values": values})
        
    requests = []
    requests.append({
        "updateCells": {
                "rows": rows,
                "fields": "note",
                "range": range_
        }
    })
    
    body = { 
             "requests": requests,
           }
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

#Parameters -> credentials, spreadsheet_id, range_(A1 Notation)
def get_user_email_address(credentials, spreadsheet_id, range_, schedule_name):
    # Call the Sheets API
    schedule = read_spreadsheet_to_df(credentials, spreadsheet_id, range_)
    if schedule is None:
        return None
    else:
        users ={}
        schedule_dict = schedule.set_index('ScheduleName').T.to_dict()
        users['notify_users'] = []
        if schedule_dict[schedule_name]['NotifyUsers']:
            users['notify_users'] = schedule_dict[schedule_name]['NotifyUsers'].split(';')
        users['alert_users'] = []
        if schedule_dict[schedule_name]['AlertUsers']:
            users['alert_users'] = schedule_dict[schedule_name]['AlertUsers'].split(';')
        return users   

#Parameters -> credentials
def add_chart(credentials, spreadsheet_id, title, grid_coordinate, axis_label, domain_grid_range_list, series_grid_range_list):
    service = build('sheets', 'v4', credentials=credentials)
    
    axis = []
    axis.append({
                "format": {
                  "bold": True,
                  "italic": True,
                  "fontSize": 24
                },
                "position": "BOTTOM_AXIS",
                "title": axis_label["bottom_axis"]
              })
    
    axis.append({
                "format": {
                  "bold": True,
                  "italic": True,
                  "fontSize": 24
                },
                "position": "LEFT_AXIS",
                "title": axis_label["left_axis"]
              })
    domains = []
    for domain_grid_range in domain_grid_range_list:
        domains.append(    {
                             "domain": { 
                                         "sourceRange": {
                                                          "sources": [domain_grid_range]
                                                        }
                                        }
                            }
                        )
    
    series = []
    for series_grid_range in series_grid_range_list:
        series.append({
                        "series": {
                                    "sourceRange":{
                                        "sources": [series_grid_range]
                                    }
                                },
                        "targetAxis": "BOTTOM_AXIS",
                           "dataLabel": {
                              "type": "DATA",
                              "textFormat": {
                                 "fontFamily": "Roboto",
                                 "fontSize": 10
                              },
                              "placement": "INSIDE_END"
                           }
                    })
    spec  = {}
    spec['title'] = title
    spec["hiddenDimensionStrategy"] = "SHOW_ALL"
    spec["basicChart"]  = { "chartType": "BAR",
                            "legendPosition": "RIGHT_LEGEND",
                            "axis": axis,
                            "domains": domains,
                            "series": series,
                            "headerCount": 1
                          }
    
    position = {}
    position['overlayPosition'] = {}
    position['overlayPosition']["anchorCell"] = grid_coordinate 
    position['overlayPosition']['offsetXPixels'] = 12
    position['overlayPosition']['offsetYPixels'] = 14
    position['overlayPosition']['widthPixels'] = 980
    position['overlayPosition']['heightPixels'] = 600
    
    requests = []
    requests.append({
                        "addChart": { "chart":{
                                                "spec": spec,
                                                "position": position,
                                            }
                                    }
                    })
    
    body = { 
             "requests": requests,
           }
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

#Parameters -> credentials
def list_files_by_name(credentials, file_name):

    drive_api = build('drive', 'v3', credentials=credentials)
    page_token = None
    query =f"mimeType ='application/vnd.google-apps.spreadsheet' and name contains '{file_name}'"
    master_files = []
    while True:
        results = drive_api.files().list( q=query,
                                         fields="nextPageToken, files(id, name, mimeType)",
                                         pageToken=page_token ).execute()
        items = results.get('files', [])
        for item in items:
            master_file = {}
            master_file["id"] = item["id"]
            master_file["name"] = item["name"]
            master_files.append(master_file)
        page_token = results.get('nextPageToken', None)
        if page_token is None:
            break
    return master_files

#Parameters -> credentials
def check_if_scheduled_now(schedule, time_now, last_ran_at ):
    if schedule['Paused'] == "Yes":
        print(f"Schedule is paused at  {time_now}")
        return False, time_now
        
    if schedule['Daily'] == "No":
        today = time_now.strftime('%A')
        if schedule[today] == "No":
            print(f"Schedule is not for today {today}")
            return False, time_now
        
    start_time = schedule['StartTime']
    end_time = schedule['EndTime']
    gap_in_hours = float(schedule['GapInHours'])
    start_time = time_now.replace(hour = int(start_time.split(':')[0]), minute=int(start_time.split(':')[1]), second=int(start_time.split(':')[2]), microsecond=0)
    end_time = time_now.replace(hour = int(end_time.split(':')[0]), minute=int(end_time.split(':')[1]), second=int(end_time.split(':')[2]), microsecond=0)
    
    next_run = start_time
    hours_to_add = datetime.timedelta(hours = gap_in_hours)


    if last_ran_at and last_ran_at.strip():
        date = last_ran_at.split(' ')[0]
        time = last_ran_at.split(' ')[1]
        last_ran_at = time_now.replace(hour = int(time.split(':')[0]), minute=int(time.split(':')[1]), second=int(time.split(':')[2]), microsecond=0)
        last_ran_at = last_ran_at.replace(day = int(date.split('-')[0]), month= datetime.datetime.strptime(date.split('-')[1], '%b').month, year=int(date.split('-')[2]))
        next_run = last_ran_at + hours_to_add

    if next_run < start_time:
        next_run = start_time

    if next_run > end_time:
        print(f"schedule FInished for the day")
        return False, time_now
    
    time_delta =  next_run - time_now
    time_delta_in_minutes = (time_delta.total_seconds())/60
    while time_delta_in_minutes < -15:
        print(f"scheduled was missed {next_run}")
        next_run = next_run + hours_to_add
        time_delta =  next_run - time_now
        time_delta_in_minutes = (time_delta.total_seconds())/60

    if abs(time_delta_in_minutes) < 15:
        return True, next_run
    else:
        print(f"Not scheduled for {time_now} Next Schedule is For {next_run}")
        return False, time_now

#Parameters -> credentials, spreadsheet_id, range_(A1 Notation)
def get_last_row_index(credentials, spreadsheet_id, range_):
    service = build('sheets', 'v4', credentials = credentials)
    data = []
    table = {
    'majorDimension': 'ROWS',
    'values': data
    }

    request = service.spreadsheets().values().append(
                            spreadsheetId= spreadsheet_id,
                            range = range_,
                            valueInputOption='USER_ENTERED',
                            insertDataOption='INSERT_ROWS',
                            body=table)

    result = request.execute()

    p = re.compile('^.*![A-Z]+\d+:[A-Z]+(\d+)$')
    match = p.match(result['tableRange'])
    last_row = match.group(1)
    return int(last_row) + 1

#Parameters -> credentials, spreadsheet_id, range_(A1 Notation), data_list
def append_row_to_sheet(credentials, spreadsheet_id, range_, data_list):
    service = build('sheets', 'v4', credentials = credentials)

    data.append(data_list)
    table = {
    'majorDimension': 'ROWS',
    'values': data
    }

    service.spreadsheets().values().append(
                                spreadsheetId = spreadsheet_id,
                                range = range_,
                                valueInputOption='USER_ENTERED',
                                insertDataOption='INSERT_ROWS',
                                body=table).execute()
