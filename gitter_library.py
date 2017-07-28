#!/usr/bin/env python
# -*- coding: utf-8 -*-

import git
import os
import pickle
import logging
from commandwrapper import WrapCommand
from logging import handlers
from configobj import ConfigObj

"""
Set the static variables and initialization
"""
CONF_FILE = "map.cfg"
CACHE_FILE = "cache.obj"
LOG_FILE = "/var/log/pytgitter.log"
BRANCH = str()
DIR_NAME = str()
REMOTE_URL = str()


def initial_config(dir_name, remote_url, branch):
    global DIR_NAME, REMOTE_URL, BRANCH
    DIR_NAME = dir_name
    REMOTE_URL = remote_url
    BRANCH = branch


class LogOperation(object):
    """
    Logger Class
    """

    def __init__(self):
        """
        First initialization
        :param url: Git Remote URL
        :param branch: Branch
        :param log_file: Log File defination
        """
        global LOG_FILE
        self.__LOGGER = logging.getLogger(__name__)
        self.__LOGGER.setLevel(logging.INFO)
        HANDLER = logging.handlers.RotatingFileHandler(
            LOG_FILE, maxBytes=20 * 1024 * 1024, backupCount=5)
        HANDLER.setLevel(logging.INFO)
        FORMATTER = logging.Formatter(
            '%(asctime)s.%(msecs)03d [%(process)s] %(levelname)s: - '
            '%(message)s', "%d/%m/%Y %H:%M:%S")
        HANDLER.setFormatter(FORMATTER)
        self.__LOGGER.addHandler(HANDLER)

    def log_error_now(self, section, message):
        """
        Error logger
        :param section: Error section
        :param message: Error log message
        :return: None
        """
        self.__LOGGER.error("\"" + section
                            + "\"" + ", out : " + "\""
                            + str(message) + "\"")

    def log_now(self, message):
        """
        Normal logger
        :param message: Log message
        :return: None
        """
        global REMOTE_URL, BRANCH
        sort_url = ".." + REMOTE_URL[-18:]
        self.__LOGGER.info(sort_url
                           + "[" + BRANCH + "]"
                           + ", " + message)

    def log_output(self, section, message):
        """
        Command output logger
        :param section: Log section
        :param message: Log message
        :return: None
        """
        self.__LOGGER.info("\""
                           + section + "\"" + ", out : "
                           + "\"" + str(message) + "\"")


class ConfigParse(object):
    """
    Config Parser Class
    """

    def __init__(self, log_object):
        """
        First initialization
        :param dir: Git directory
        :param url: Git remote url
        :param branch: branch
        :param log_object: created log object
        """
        global CONF_FILE, DIR_NAME, REMOTE_URL, BRANCH, LOG_FILE
        self.__config_db = ConfigObj(CONF_FILE)
        self.__branch = BRANCH
        self.__url = REMOTE_URL
        self.__dir = DIR_NAME
        self.__log_object = log_object

    def read_map(self):
        """
        Create all config
        :return:
        """
        return_map = list()
        for git_url, value in self.__config_db.iteritems():
            temp_dict = dict()
            temp_dict["url"] = git_url
            temp_dict["branch"] = value.keys()[0]
            temp_dict["dir"] = value.get(value.keys()[0]).keys()[0]
            return_map.append(temp_dict)
        return return_map


    def get_maps(self):
        """
        Return map list from loaded config parse object
        :return: List
        """
        return_map = dict()
        try:
            for key, value in self.__config_db[self.__url][self.__branch][self.__dir].iteritems():
                return_map[key] = value
            return return_map
        except Exception as e:
            self.__log_object.log_error_now("ConfigParse", e)
            return False


class Last(object):
    """
    Last Information Object Class
    """
    global CACHE_FILE
    __cache_data = dict()
    __new_data = str()
    __cache_file = CACHE_FILE

    def __init__(self, new_data):
        """
        First initialization
        :param new_data: New data to write
        """
        self.__new_data = new_data
        if os.path.isfile(self.__cache_file):
            file_open = open(self.__cache_file, 'rb')
            self.__cache_data = pickle.load(file_open)
            file_open.close()
        else:
            self.__new_data = dict()
            self.push_cache_data()

    def get_cache_data(self):
        """
        Return old info object from file
        :return:
        """
        return self.__cache_data

    def push_cache_data(self):
        """
        Push new info to object file
        :return:
        """
        try:
            write_file = open(self.__cache_file, 'wb')
            pickle.dump(self.__new_data, write_file)
            write_file.close()
            return True
        except Exception as e:
            return False


class Giter(object):
    """
    Git Operation Class
    """
    __is_new = False

    def __init__(self):
        """
        First initialization
        :param dir: Git directory
        :param url: Git remote url
        :param branch: Branch
        """
        global DIR_NAME, REMOTE_URL, BRANCH
        self.__current_commit = ""
        if os.path.isdir(DIR_NAME):
            self.__branch = BRANCH
            self.__url = REMOTE_URL
            self.__dir = DIR_NAME
            self.__repository = git.Repo(DIR_NAME)
        else:
            os.mkdir(DIR_NAME)
            self.__repository = git.Repo.init(DIR_NAME)
            self.__repository.create_remote('origin', REMOTE_URL).fetch()
            self.__repository.remote().pull(BRANCH)
            self.__repository.git.checkout(BRANCH)
            self.__is_new = True

    def get_last_commit(self):
        """
        Get local last commit number from git dir.
        :return: String
        """
        if not self.__is_new:
            sha = self.__repository.head.object.hexsha
            self.__current_commit = str(self.__repository.rev_parse(sha))
        else:
            self.__current_commit = "NA"
        return self.__current_commit

    def pull_and_get(self):
        """
        Git pull from local directory and get the
        git last commit number
        :return: String
        """
        if not self.__is_new:
            self.__repository.git.clean('-fd')
            self.__repository.remote().fetch()
            self.__repository.remote().pull(self.__branch)
        diff = self.__repository.git.diff(
            'HEAD~1..HEAD', name_only=True)
        return_list = []
        for i in str(diff).split("\n"):
            return_list.append(i)
        return return_list


class RunCommand(object):
    """
    Command Run Class
    """

    def __init__(self, log_object):
        """
        First initialization
        :param log_object: created log object
        """
        self.__log_object = log_object

    def run_now(self, commands):
        """
        Command run method
        :param commands: All command list
        :return: None
        """
        for command in commands:
            command_obj = WrapCommand(command, shell=True)
            command_obj.start()
            command_obj.join()
            if command_obj.returncode != 0:
                self.__log_object.log_error_now(command, command_obj.results)
            else:
                self.__log_object.log_output(command, command_obj.results)