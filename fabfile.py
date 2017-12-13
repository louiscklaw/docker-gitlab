#!/usr/bin/env python
# coding:utf-8
import os
import sys
import logging
import traceback
from pprint import pprint

from fabric.api import *
from fabric.colors import *

LOGGING_FORMATTER = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
formatter = logging.Formatter(LOGGING_FORMATTER)

logging.basicConfig(
    level=logging.DEBUG,
    format=LOGGING_FORMATTER,
    datefmt='%d %m %Y %H:%M:%S',
    filename='%s' % __file__.replace('.py', '.log'),
    filemode='a')

# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
# set a format which is simpler for console use

console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

env.hosts = ['192.168.88.6']


@task
def rebuild_container():

    PROJ_HOME = 'docker-gitlab'

    LOCAL_DIR, REMOTE_DIR = (
        '/home/logic/_workspace/docker-files/%s' % PROJ_HOME,
        '/srv/docker-files/%s' % PROJ_HOME
    )

    local(
        'rsync -avrPz --exclude .git --exclude .vscode %s/ logic@192.168.88.6:%s' % (LOCAL_DIR, REMOTE_DIR))

    with cd(REMOTE_DIR):
        run('docker-compose build')
    #     run('docker-compose kill')
    #     run('docker-compose up --remove-orphans  -d')
    #     run('docker-compose ps')


@task
def run_test():
    """to run the behave test"""

    # STEP: run the test
    print(green("STEP: run the test", True))

    test_feautre_files = [
        './feature'

    ]

    env.allure_report_directory = './_allure_result'
    allure_present_command = 'allure serve %s' % env.allure_report_directory

    for test_feature_file in test_feautre_files:
        behave_command = 'behave --no-capture -f allure_behave.formatter:AllureFormatter -o %s %s' % (
            env.allure_report_directory, test_feature_file)

        with settings(warn_only=True):
            local(behave_command)

    local(allure_present_command)


@task
def start_android_emulator():
    # emulator -avd Nexus_5X_API_24

    pass
