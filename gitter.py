#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import gitter_library
from time import time as _time

"""
Set the static variables
"""
DIR_NAME = "/tmp/test"
REMOTE_URL = "https://git.blablablabla.com/repouser/test.git"
BRANCH = "master"
FLD_PTRN = "FOLDER:"
PID = "/var/run/pytgitter.pid"
LOG_FILE = "/var/log/pytgitter.log"

"""
Set the static objects
"""
PID_CLEAR_TIME = 60 * 60 * 24 * 7
all_commands = list()
folder_commands = list()
LogOps = gitter_library.LogOperation(url=REMOTE_URL, branch=BRANCH, log_file=LOG_FILE)


"""
Running control
"""
"""

def PID_OVER_WRITER():
    os.mknod(PID)
    pid = str(os.getpid())
    pid_write = open(PID, 'a')
    pid_write.write(pid)
    pid_write.close()


if os.path.isfile(PID):
    # Append the 7 day
    fileTime = os.path.getmtime(PID) + PID_CLEAR_TIME
    nowTime = _time()
    pidLast = open(PID, 'r')
    lastPidNum = pidLast.read().rstrip(os.linesep)
    pidLast.close()
    if fileTime > nowTime:
        LogOps.log_now("Running another whitelist instance -> %s", lastPidNum)
        sys.exit(0)
    else:
        LogOps.log_now("PytGitter instance 7 days inactive, pid %s cleaned and starting..",
                       lastPidNum)
        os.system('kill -9 ' + lastPidNum)
        os.remove(PID)
        PID_OVER_WRITER()
else:
    PID_OVER_WRITER()
"""

"""
Create class objects from library
"""
Giter = gitter_library.Giter
ConfigParse = gitter_library.ConfigParse(dir=DIR_NAME, url=REMOTE_URL,
                                         branch=BRANCH, log_object=LogOps)
RunCommands = gitter_library.RunCommand(log_object=LogOps)

"""
Collecting All required data
"""
try:
    file_map = ConfigParse.get_maps()
    # Static file map
    old_commit = Giter(dir=DIR_NAME, url=REMOTE_URL,
                       branch=BRANCH).get_last_commit()
    # Get old commit hash
    changed_files = Giter(dir=DIR_NAME, url=REMOTE_URL,
                          branch=BRANCH).pull_and_get()
    # Changed files after fetch and pull operation
    new_unlikely_commit = Giter(dir=DIR_NAME, url=REMOTE_URL,
                                branch=BRANCH).get_last_commit()
    # Get end (new or old ?) commit hash
except Exception as e:
    LogOps.log_error_now("Collect Operation", e)
    sys.exit(1)

"""
Control and running
"""
if old_commit != new_unlikely_commit:
    # if changed ?
    LogOps.log_now("Change detected! (" + old_commit + " to " + new_unlikely_commit + ")")
    for key, commands in file_map.iteritems():
        # loop the static map list
        if key == "ALL":
            # if all command ?
            all_commands = commands
        elif str(key).__contains__(FLD_PTRN):
            # if specific folder ?
            folder_name = str(key).split(FLD_PTRN)[1]
            for sear_item in changed_files:
                if folder_name in sear_item:
                    folder_commands.extend(commands)
        else:
            # and another rule is specific file
            if key in changed_files:
                # if specific file ?
                RunCommands.run_now(commands)
    if folder_commands.__len__() > 0:
        # Folder command run the end of process
        RunCommands.run_now(list(set(folder_commands)))
    if all_commands.__len__() > 0:
        # All command run the end of process
        RunCommands.run_now(all_commands)
else:
    LogOps.log_now("No Change.. (" + old_commit + ")")
