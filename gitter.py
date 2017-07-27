#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import gitter_library

"""
Set the static variables
"""
FLD_PTRN = "FOLDER:"
PID = "/var/run/pytgitter.pid"

"""
Set the static objects
"""
PID_CLEAR_TIME = 60 * 60 * 24 * 7
all_commands = list()
folder_commands = list()
LogOps = gitter_library.LogOperation()

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


def git_now(remote_url, branch, dir_name):
    global Gitter, LogOps
    gitter_library.initial_config(dir_name, remote_url, branch)
    Giter = gitter_library.Giter
    ConfigParse = gitter_library.ConfigParse(log_object=LogOps)
    RunCommands = gitter_library.RunCommand(log_object=LogOps)

    try:
        file_map = ConfigParse.get_maps()
        # Static file map
        old_commit = Giter().get_last_commit()
        # Get old commit hash
        changed_files = Giter().pull_and_get()
        # Changed files after fetch and pull operation
        new_unlikely_commit = Giter().get_last_commit()
        # Get end (new or old ?) commit hash
    except Exception as e:
        LogOps.log_error_now("Collect Operation", e)
        sys.exit(1)

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


if __name__ == '__main__':
    ConfigParse = gitter_library.ConfigParse(log_object=LogOps)
    for map_dict in ConfigParse.read_map().__iter__():
        url = map_dict["url"]
        dir = map_dict["dir"]
        branch = map_dict["branch"]
        git_now(url, branch, dir)