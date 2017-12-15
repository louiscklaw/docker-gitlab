#!/usr/bin/env python3
"""
taskfile for docker-gitlab building
"""

# from invoke import run,task
import os
# import sys

from datetime import datetime
from fabric.api import run, cd, env, task, local, prefix,settings
from fabric.colors import *
import re

env.hosts = ['192.168.88.6']

CURR_DIRECTORY = os.path.dirname(__file__)

DOCKER_CONTAINER = r'docker-letsencrypt-manager'
PATH_DOCKER_FILE_DIRECTORY = r'/srv/docker-files'

PATH_CONTAINER_DIRECTORY = os.path.join(
    PATH_DOCKER_FILE_DIRECTORY, DOCKER_CONTAINER)

# file for git to ignore
PATH_NOT_FOR_VERSIONING = []
PATH_NOT_FOR_VERSIONING.append(
    PATH_CONTAINER_DIRECTORY + r'/./etc/letsencrypt/')

EPOCH_DATETIME = datetime.now().strftime('%s')

env.use_ssh_config = True


PROJ_HOME = 'docker-gitlab'
LOCAL_DIR, REMOTE_DIR = (
    '/home/logic/_workspace/docker-files/%s' % PROJ_HOME,
    '/srv/docker-files/%s' % PROJ_HOME
)

GITLAB_SERVICE_NAME = 'gitlab'

@task
def sync_files():
    """to sync file between develop machine and the docker host"""
    local(
        'rsync -avrPz --exclude .git --exclude .vscode %s/ logic@192.168.88.6:%s' % (LOCAL_DIR, REMOTE_DIR))

def gitrunner_register():
    run('docker-compose exec gitlab_shell_runner gitlab-runner')

def parse_gitrunner_list(list_input):
    pattern=r'(?P<m_reg_name>.+?)\s+Executor=(?P<m_executor>.+?) Token=(?P<m_token>.{0,30}) URL=(?P<m_url>.+)'
    # pattern=r'(?P<m_reg_name>.+?)\s+Executor'
    ms = re.findall(pattern, list_input)
    return ms

def gitrunner_list_unregister_all(container_name):

    registration_list = run('docker-compose exec %s gitlab-runner list' % container_name)

    # remove ansi color cod
    registration_list = registration_list.replace('\x1b[0;m','')

    parsed_list = parse_gitrunner_list(registration_list)
    for m in parsed_list:
        (reg_name, executor, token, url) = m
        # gitlab-runner unregister -t ab13234665cd17f538efe718a6a177 -u https://repo.louislabs.com/
        with settings(warn_only=True):
            run('docker-compose exec %s gitlab-runner unregister -t %s  -u %s ' % (container_name, token, url))

def rebuild_gitlab(gitlab_container_name):
    print(green('building gitlab', True))
    with cd(REMOTE_DIR):
        run('docker-compose up -d --remove-orphans %s' % gitlab_container_name)
        # run('docker-compose exec %s gitlab-rake gitlab:env:info' % gitlab_container_name)
        # run('docker-compose exec %s gitlab-rake gitlab:check SANITIZE=true' % gitlab_container_name)

def rebuild_gitlab_runner(container_name):
    print(green('building gitlab runner', True))
    with cd(REMOTE_DIR), prefix('source .env'):
        run('docker-compose up -d --remove-orphans %s' % container_name)

def print_gitlab_runner(container_name):
        with settings(warn_only=True):
            run('docker-compose exec %s gitlab-runner list' % container_name)
            run('docker-compose exec %s gitlab-runner verify --delete' % container_name)
            run('docker-compose exec %s gitlab-runner unregister --all-runners' % container_name)
            run('docker-compose exec %s gitlab-runner list' % container_name)

            run('docker-compose exec %s gitlab-runner register --non-interactive --name shell_runner --url https://repo.louislabs.com/ --registration-token $REG_TOKEN --executor shell' % container_name)

@task
def rebuild_container():

    sync_files()
    GITLAB_NAME = 'gitlab'
    GITLAB_IMAGE_NAME = 'gitlab/gitlab-ce'

    GITLAB_RUNNER_NAME = 'gitlabrunner'
    GITLAB_SHELL_RUNNER_NAME = 'gitlab_shell_runner'

    GITLAB_RUNNER_CONTAINER = os.path.sep.join([
        REMOTE_DIR, GITLAB_RUNNER_NAME
    ])

    # print(green('rebuild gitlabrunner base image'))
    # run('docker build -t gitlabrunner:latest %s' % GITLAB_RUNNER_CONTAINER )

    with cd(REMOTE_DIR):
        run('docker-compose build')
        run('docker-compose down  --remove-orphans')
        rebuild_gitlab(GITLAB_NAME)
        rebuild_gitlab_runner(GITLAB_SHELL_RUNNER_NAME)

        run('docker-compose ps')


@task
def reload_config():
    with cd(REMOTE_DIR):
        run('docker-compose exec %s /bin/bash gitlab-ctl reconfigure' % GITLAB_SERVICE_NAME)
        # run('docker exec -it gitlab update-permissions')
        run('docker-compose ps')
