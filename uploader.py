# learning_modules/uploader.py
from django.conf import settings
from django.contrib import messages
import zipfile
import os
import xml.dom.minidom
import json
from xml.dom.minidom import Node
from learning_modules.models import Module, Section, Activity  

# TODO translate langs for 
def handle_uploaded_file(f,request):
    if f.content_type != 'application/zip':
        messages.info(request,"You may only upload a zip file")
        # TODO delete file
        return False
    zipfilepath = settings.MODULE_UPLOAD_DIR + f.name
    with open(zipfilepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    zip = zipfile.ZipFile(zipfilepath)
    zipextractpath = settings.MODULE_UPLOAD_DIR + '/temp/'
    zip.extractall(path=zipextractpath)      
    
    mod_name = ''
    for dir in os.listdir(zipextractpath)[:1]:
        mod_name = dir
       
    # check there is at least a sub dir 
    if mod_name == '':
        messages.info(request,"Invalid module zip file")
        # TODO delete file
        # TODO delete temp folder
        return False
    
    # check that the 
    if not os.path.isfile(zipextractpath + mod_name + "/module.xml"):
        messages.info(request,"Zip file does not contain a module.xml file")
        # TODO delete file
        # TODO delete temp folder
        return False
      
    # parse the module.xml file
    doc = xml.dom.minidom.parse(zipextractpath + mod_name + "/module.xml") 
    for meta in doc.getElementsByTagName("meta")[:1]:
        versionid = 0
        for v in meta.getElementsByTagName("versionid")[:1]:
            versionid = int(v.firstChild.nodeValue)
        temp_title = {}
        for t in meta.getElementsByTagName("title"):
            temp_title[t.getAttribute('lang')] = t.firstChild.nodeValue
        title = json.dumps(temp_title)
        shortname = ''
        for sn in meta.getElementsByTagName("shortname")[:1]:
            shortname = sn.firstChild.nodeValue
    
    # Find if module already exists
    try:
        module = Module.objects.get(shortname = shortname)
        # check if module version is older
        if module.version > versionid:
            messages.info(request,"A newer version of this module already exists")
            # TODO delete temp folder
            return False
        module.title = title
        module.version = versionid
        module.user = request.user
        module.filename = f.name
        module.save()
    except Module.DoesNotExist:
        module = Module()
        module.shortname = shortname
        module.title = title
        module.version = versionid
        module.user = request.user
        module.filename = f.name
        module.save()
    # TODO delete temp folder
    return True       
              