#!/usr/bin/env python
import os, time, sys
from django.conf import settings

def run():
    print 'Starting cron for learning modules'
    now = time.time()
    path = settings.MODULE_UPLOAD_DIR + "temp"
    for f in os.listdir(path):
        f = os.path.join(path, f)
        if os.stat(f).st_mtime < now - 3600*6:
            print f
            if os.path.isfile(f):
                os.remove(f)
                
    print 'Cron ended for learning modules'
    return

if __name__ == "__main__":
    run()