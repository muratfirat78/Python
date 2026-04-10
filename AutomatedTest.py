from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from IPython.utils.process import shutil
import os, json
import gdown
import warnings
import google.auth

import httplib2
from google.auth import default as get_default_credentials
from google_auth_httplib2 import AuthorizedHttp

student_name = None
student_no = None

input_files = ['curssengedaan.json','cursusaanbod.json','test-3-curssengedaan.json'
                ,'test-2-curssengedaan.json','test-1-curssengedaan.json']
source_directory ='/content/'
uploaded_files = []
test_passes = dict()
gitfolder = 'https://raw.githubusercontent.com/muratfirat78/Python/refs/heads/main/'
folderid = '1N0-wGAv9SBTmQ0FdVC0wyqrJ_NcXgJR1'
auth.authenticate_user()  
drive_service = build('drive', 'v3')
    

def CheckPass(student_name,student_no):

    global drive_service 
    
    query = f"'{folderid}' in parents and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    for file in files:
        print(file['name'],student_name,student_no)
        if (student_name in file['name']) and (str(student_no) in file['name']):
            return True

    return False


def to_json(trg_dir,dictionary, filename):

  with open(trg_dir+"/"+filename,'w') as fp:
      json.dump(dictionary, fp,sort_keys=True, indent=4,ensure_ascii=False)

def checkTest(student_name,student_no,curr_dict,testno,uploaded_files):

    global test_passes,source_directory
   

    current_key = 'key_case_'+str(testno)+'.json'
    key_dict = dict()
    for filename in os.listdir(source_directory):
        if filename == current_key:
            with open(source_directory+"/"+filename, 'r') as file:
                key_dict = json.load(file)

    testsuccess = 0
    if len(curr_dict) == len(key_dict):
        for quartile,course in key_dict.items():
            if curr_dict[int(quartile)] == course:
                testsuccess+=1
        if testsuccess == len(key_dict):
            test_passes[testno] = True
            print("Test case",testno,"passed!")
       
            if len(test_passes) == 4:  # if all tests passed:
                print("All test passed, congrats!")
                finalize(student_name,student_no,uploaded_files)
                return 
        else:
            test_passes[testno] = False
            print("Test case",testno,"failed")
            print("It seems better to improve your solution and make tests again, good luck!")
            return 
    else:
        print("Test case",testno,"failed")
        print("It seems better to improve your solution and make tests again, good luck!")
        test_passes[testno] = False
        return
        
def finalize(student_name,student_no,uploaded_files):

    global folderid,source_directory
    
    auth.authenticate_user()  

  
    #SCOPES = ['https://www.googleapis.com/auth/drive.metadata', 'https://www.googleapis.com/auth/drive']

    #credentials, project_id = google.auth.default(scopes=SCOPES)

   

    # http timeout and credential
    credentials, _ = get_default_credentials()
    http_with_timeout = httplib2.Http(timeout=3600)
    authed_http = AuthorizedHttp(credentials, http=http_with_timeout)

    drive_service = build('drive', 'v3')

    fid = '1IU1biWrDLZ7J7hWaZRJrQDCaFQPvlc1r'
    
    query = f"'{fid}' in parents and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    
    for file in files:
        print(file['id'], file['name'])

    
    for filename in os.listdir(source_directory):

        
        if filename in uploaded_files:

            file_metadata = {'name': student_name+"_"+str(student_no)+"_"+filename,'mimeType': 'text/x-python','parents': [folderid]}

            media = MediaFileUpload(source_directory+'/'+filename,mimetype='text/x-python')
            
            created = drive_service.files().create(body=file_metadata,media_body=media,fields='id').execute()

  


    return