import os
from time import sleep

with open("applist.txt",'r') as applist:
    os.system("adb connect 192.168.4.10")
    for app in applist.readlines():
        print("adb shell am force-stop {appname}".format(appname=app.strip()))
        os.system("adb shell am force-stop {appname}".format(appname=app.strip()))
        sleep(0.1)
    os.system("adb disconnect 192.168.4.10")