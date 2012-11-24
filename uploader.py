# learning_modules/uploader.py
from django.conf import settings
from django.contrib import messages
import zipfile
import os

# TODO translate langs for 
def handle_uploaded_file(f,request):
    if f.content_type != 'application/zip':
        messages.info(request,"You may only upload a zip file")
        return False
    zipfilepath = settings.MODULE_UPLOAD_DIR + f.name
    with open(zipfilepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    zip = zipfile.ZipFile(zipfilepath)
    zipextractpath = '/home/alex/temp/temp/'
    zip.extractall(path=zipextractpath)      
    
    mod_name = ''
    for dir in os.listdir(zipextractpath)[:1]:
        messages.info(request,dir)
        mod_name = dir
        
    if mod_name == '':
        messages.info(request,"Invalid module zip file")
        return False
    if not os.path.isfile(zipextractpath + mod_name + "/module.xml"):
        messages.info(request,"Zip file does not contain a module.xml file")
        return False
        
    return True       
    
             