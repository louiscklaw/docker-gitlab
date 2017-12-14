#!/usr/bin/env python
"""
taskfile for docker-gitlab building
"""

# from invoke import run,task
import os
# import sys

from datetime import datetime
from fabric.api import run, cd, env, task, local

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
def rebuild_container():

    local(
        'rsync -avrPz --exclude .git --exclude .vscode %s/ logic@192.168.88.6:%s' % (LOCAL_DIR, REMOTE_DIR))

    with cd(REMOTE_DIR):
        run('docker-compose up --remove-orphans  -d')
        # run('docker exec -it gitlab update-permissions')
        run('docker-compose ps')

@task
def reload_config():
    with cd(REMOTE_DIR):
        run('docker-compose exec %s /bin/bash gitlab-ctl reconfigure' % GITLAB_SERVICE_NAME)
        # run('docker exec -it gitlab update-permissions')
        run('docker-compose ps')
