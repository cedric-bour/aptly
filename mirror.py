#!/usr/bin/python3 -u

import re
import time
from datetime import datetime
import pytz

import aptly as aptly

print()
print("Initial repos...")
for repo in aptly.repos:
    for distribution in repo["distributions"]:
        repo_name = repo["name"] + '-' + re.sub('[^A-Za-z0-9-_]+', '', distribution)
        now = datetime.now(pytz.timezone("Europe/Paris") )
        now_str = now.strftime("%D:%m:%Y %H:%M:%S")
        print()

        print('[' + now_str + '] ' + repo_name + ": Add repo")
        aptly.mirror_create(repo_name, repo["url"], distribution, repo["components"], repo["archs"])

        print('[' + now_str + '] ' + repo_name + ": Update repo")
        aptly.mirror_update(repo_name, repo["archs"])

        print('[' + now_str + '] ' + repo_name + ": Snap repo")
        aptly.snap_create(repo_name, repo_name)

        print('[' + now_str + '] ' + repo_name + ": Publish repo")
        aptly.publish_snap(repo_name, repo["url"], repo["override_path"] if "override_path" in repo else '')

print()
print("Update repos...")
last_day = 0
while True:
    for repo in aptly.repos:
        for distribution in repo["distributions"]:
            now = datetime.now(pytz.timezone("Europe/Paris") )
            if last_day != now.day:
                now_str = now.strftime("%D:%m:%Y %H:%M:%S")
                repo_name = repo["name"] + '-' + re.sub('[^A-Za-z0-9-_]+', '', distribution)
                print()

                print('[' + now_str + '] ' + repo_name + ": Update repo [update]")
                aptly.mirror_create(repo_name, repo["url"], distribution, repo["components"], repo["archs"])

                print('[' + now_str + '] ' + repo_name + ": Create new snap of repo [update]")
                aptly.snap_create(repo_name, repo_name + '_up')

                print('[' + now_str + '] ' + repo_name + ": Publish new snap of repo [update]")
                aptly.publish_switch(repo_name + '_up', repo["url"], distribution, repo["override_path"] if "override_path" in repo else '')

                print('[' + now_str + '] ' + repo_name + ": Drop original snap of repo [update]")
                aptly.snap_drop(repo_name)
                
                print('[' + now_str + '] ' + repo_name + ": Create final snap of repo [update]")
                aptly.snap_create(repo_name, repo_name)

                print('[' + now_str + '] ' + repo_name + ": Publish final snap of repo [update]")
                aptly.publish_switch(repo_name, repo["url"], distribution, repo["override_path"] if "override_path" in repo else '')

                print('[' + now_str + '] ' + repo_name + ": Drop secondary snap of repo [update]")
                aptly.snap_drop(repo_name + '_up')

    if last_day != now.day:
        last_day = now.day
        print()
        print("Wait 24h before next update")

    time.sleep(3600)