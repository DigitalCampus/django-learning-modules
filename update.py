#!/usr/bin/env python
from datetime import datetime

from learning_modules.models import Tracker, Activity, Media

def run():
    print 'Starting '
    trackers = Tracker.objects.all()
    for t in trackers:
        try:
            activity = Activity.objects.get(digest=t.digest)
            t.module = activity.section.module
            t.type = activity.type
            t.save()
        except Activity.DoesNotExist:
            pass
        
        try:
            media = Media.objects.get(digest=t.digest)
            t.module = media.module
            t.type = 'media'
            t.save()
        except Media.DoesNotExist:
            pass
    return

if __name__ == "__main__":
    run()
