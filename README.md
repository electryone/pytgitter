# PytGitter

PytGitter is a git tracker tool, designed to execute commands for these while monitoring the changes on the branch.

Features :
  - Git branch change tracking
  - Executing specific commands on file and folder based (any and every) changes
  - Logging change and run attempt to file
  - Multiple git repository usage

Supported OS :
  - Linux
  - Mac OS X

# Preparation :
- Pull this project
- pip install -r requirements.txt
- gitter.py file add to crontab. Every 2 minutes example:
    "*/2 * * * * root python /path/pytgitter/gitter.py"

# Usage :
- Edit the map.cfg file with examples (in this file)
```vim
#
# PytGitter static file map
#
# Usage :
# [git full http url]
# [[git branch name]]
# [[[git folder path]]]
# ALL = "command", "command2", "command3", ... (Processes for All files)
# file = "command", "command2", "command3", ... (Processes for Specific files)
# folder/ ="command", "command2", "command3", ... (Processes for Specific files in directory)
#
# NOTE : Do not forget to add "," after commands
#
```
- Cron service reload/restart
- You can see changes in "/var/log/pytgitter.log" file
    "tail -f /var/log/pytgitter.log"
```sh
15/07/2017 11:22:38.365 [18260] INFO: - ..pytgitter/testere.git[master], No Change.. (e22675c25a903f2ea25b6ab871d5d1d259357e1f)
15/07/2017 11:23:34.758 [18331] INFO: - ..pytgitter/testere.git[master], Change detected! (e22675c25a903f2ea25b6ab871d5d1d259357e1f to 1665c56c1dda31f40519e9ae124b87014d47e46a)
15/07/2017 11:23:34.795 [18331] INFO: - "ls -al", out : "gitter.py
gitter.pyc
gitter_library.py
map.cfg
requirements.txt
"
```

License
----

GNU
