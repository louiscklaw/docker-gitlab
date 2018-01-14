#!/usr/bin/env python3
"""
taskfile for docker-gitlab building
"""

# from invoke import run,task
import os
import sys
# import sys

from datetime import datetime
from fabric.api import run, cd, env, task, local, prefix, settings, quiet
from fabric.colors import *
import re

import time

env.hosts = ['192.168.88.6']
REG_TOKEN = os.getenv('REG_TOKEN', 'NOT_DEFINED')


CURR_DIRECTORY = os.path.dirname(__file__)

DOCKER_CONTAINER = r'docker-gitlab'
PATH_DOCKER_FILE_DIRECTORY = r'/srv/docker-files'

PATH_CONTAINER_DIRECTORY = os.path.join(PATH_DOCKER_FILE_DIRECTORY, DOCKER_CONTAINER)

# file for git to ignore
PATH_NOT_FOR_VERSIONING = []
PATH_NOT_FOR_VERSIONING.append(PATH_CONTAINER_DIRECTORY + r'/./etc/letsencrypt/')

EPOCH_DATETIME = datetime.now().strftime('%s')


env.use_ssh_config = True


PROJ_HOME = 'docker-gitlab'
LOCAL_DIR, REMOTE_DIR = (
    '/home/logic/_workspace/docker-files/%s' % PROJ_HOME,
    '/srv/docker-files/%s' % PROJ_HOME
)

GITLAB_SERVICE_NAME = 'gitlab'

GITLAB_NAME = 'gitlab'
GITLAB_IMAGE_NAME = 'gitlab/gitlab-ce'

RUNNER_CONTAIENR = 'runner-container'
GITLAB_RUNNER_NAME = 'gitlab-runner'
# GITLAB_SHELL_RUNNER_NAME = 'gitlab_shell_runner'
BEHAVE_RUNNER_NAME = 'behave-runner'

GITLAB_RUNNER_CONTAINER = os.path.sep.join([
    REMOTE_DIR, RUNNER_CONTAIENR, GITLAB_RUNNER_NAME
])
BEHAVE_RUNNER_CONTAINER = os.path.sep.join([
    REMOTE_DIR, RUNNER_CONTAIENR, BEHAVE_RUNNER_NAME
])


def form_parameter_string(parameters):
    return ' '.join(
        para_name + ' ' + para_value for para_name, para_value in parameters.items()
    )


class docker_command():
    def __init__(self, service_name):
        self.service_name = service_name
        pass

    def docker_compose(self, options='', commands=''):
        try:
            command = 'docker-compose %s %s %s' % (
                commands, options, self.service_name)
            return run(command)
        except Exception as e:
            print(command)
            raise e
        else:
            pass


class docker_container():
    def __init__(self, service_name):
        self.service_name = service_name

    def _up_docker_compose(self):
        print(green('building %s' % self.service_name))
        # run('docker-compose up -d --remove-orphans %s' % self.service_name)
        docker_command(self.service_name).docker_compose(
            '--remove-orphans', 'up -d')
        print(green('build %s done' % self.service_name, True))

    def _build_docker_compose(self):
        print(green('building %s' % self.service_name))
        # run('docker-compose up -d --remove-orphans %s' % self.service_name)
        docker_command(self.service_name).docker_compose('', 'build')
        print(green('build %s done' % self.service_name, True))

    def build_container(self):
        with settings(warn_only=True), cd(REMOTE_DIR), prefix('source .env'):
            self._build_docker_compose()
            self._up_docker_compose()

    def start_container(self):
        try:
            with settings(warn_only=True), cd(REMOTE_DIR), prefix('source .env'):
                run('docker-compose up -d --remove-orphans %s' %
                    self.service_name)
        except Exception as e:
            raise e
        else:
            pass


class allure_report_container(docker_container):
    def __init__(self, service_name):
        self.service_name = service_name
        pass


# @task
# def sync_files():
#     """to sync file between develop machine and the docker host"""
#     exclude_list = [
#         '.git', '.vscode', 'etc', 'root', 'usr'
#     ]
#     exclude_string = ' '.join([
#         '--exclude %s' % _ for _ in exclude_list
#     ])
#     local(
#         'rsync -avrPz %s %s/ logic@192.168.88.6:%s' % (exclude_string, LOCAL_DIR, REMOTE_DIR))

@task
def sync_files():
    """to sync file between develop machine and the docker host"""
    exclude_list = [
            '.git', '.vscode', 'etc', 'root', 'usr'
        ]
    rsync_project(
        local_dir = LOCAL_DIR+'/',
        remote_dir = REMOTE_DIR,
        exclude=exclude_list
    )


def gitrunner_register():
    run('docker-compose exec gitlab_shell_runner gitlab-ci-multi-runner')


def parse_gitrunner_list(list_input):
    pattern = r'(?P<m_reg_name>.+?)\s+Executor=(?P<m_executor>.+?) Token=(?P<m_token>.{0,30}) URL=(?P<m_url>.+)'
    # pattern=r'(?P<m_reg_name>.+?)\s+Executor'
    ms = re.findall(pattern, list_input)
    return ms


def gitrunner_list_unregister_all(container_name):

    registration_list = run(
        'docker-compose exec %s gitlab-ci-multi-runner list' % container_name)

    # remove ansi color cod
    registration_list = registration_list.replace('\x1b[0;m', '')

    parsed_list = parse_gitrunner_list(registration_list)
    for m in parsed_list:
        (reg_name, executor, token, url) = m
        # gitlab-ci-multi-runner unregister -t ab13234665cd17f538efe718a6a177 -u https://repo.louislabs.com/
        with settings(warn_only=True):
            run('docker-compose exec %s gitlab-ci-multi-runner unregister -t %s  -u %s ' %
                (container_name, token, url))


def rebuild_gitlab_container(gitlab_container_name):
    print(green('building gitlab', True))
    with cd(REMOTE_DIR), quiet():
        run('docker-compose up -d --remove-orphans %s' % gitlab_container_name)
        # run('docker-compose exec %s gitlab-rake gitlab:env:info' % gitlab_container_name)
        # run('docker-compose exec %s gitlab-rake gitlab:check SANITIZE=true' % gitlab_container_name)


def normalize_to_list(variant):
    output = variant
    if type(output) == type([]):
        pass
    else:
        output = [output]
    return output


def register_gitlab_runner(container_name, tags_list):

    tags_list = normalize_to_list(tags_list)

    parameters = {
        '--non-interactive': '',
        '--executor': 'shell',
        '--name': container_name,
        '--tag-list': ','.join(tags_list),
        '--url': 'https://repo.louislabs.com',
        '--registration-token': REG_TOKEN
    }

    with settings(warn_only=True):
        run('docker-compose exec {container_name} gitlab-ci-multi-runner register {para}'.format(
            container_name=container_name,
            para=form_parameter_string(parameters)
        )
        )


def rebuild_runner(container_name, tags_list):
    print(green('building gitlab runner', True))
    with cd(REMOTE_DIR), prefix('source .env'), quiet():
        run('docker-compose build %s' % container_name)
        run('docker-compose up -d --remove-orphans %s' % container_name)

    unregister_gitlab_runner(container_name)
    register_gitlab_runner(container_name, tags_list)


def unregister_gitlab_runner(container_name):
    with settings(warn_only=True):
        run('docker-compose exec %s gitlab-ci-multi-runner list' % container_name)
        run('docker-compose exec %s gitlab-ci-multi-runner verify --delete' % container_name)
        run('docker-compose exec %s gitlab-ci-multi-runner unregister --all-runners' % container_name)
        run('docker-compose exec %s gitlab-ci-multi-runner list' % container_name)


def gitlab_check(container_name):
    with cd(REMOTE_DIR):
        run('docker-compose exec %s /bin/bash gitlab-rake gitlab:check' % container_name)


@task
def reload_config():
    sync_files()

    with cd(REMOTE_DIR):
        gitlab_check(GITLAB_SERVICE_NAME)
        run('docker-compose exec %s /bin/bash gitlab-ctl reconfigure' %
            GITLAB_SERVICE_NAME)
        gitlab_check(GITLAB_SERVICE_NAME)
        # run('docker exec -it gitlab update-permissions')
        run('docker-compose ps')


def rebuild_runner_image():
    print(green('building gitlabrunner image'))
    with cd(GITLAB_RUNNER_CONTAINER):
        # with cd(REMOTE_DIR), prefix('source .env'):
        print(green('start runner building'))
        run('docker build -t gitlabrunner .')
        print(green('building done'))

    with cd(BEHAVE_RUNNER_CONTAINER):
        print(green('start runner building'))
        # rebuild_gitlab_runner(runner_name, ['behave',android_api])
        run('docker build -t behave-runner .')
        print(green('building done'))


# def rebuild_gitlab_shell_runner():
#     with cd(REMOTE_DIR), prefix('source .env'):
#         print(green('start runner building'))
#         rebuild_gitlab_runner(GITLAB_SHELL_RUNNER_NAME, ['basic'])
#         print(green('building done'))


def rebuild_beahve_runner(runner_name, android_api):
    # with cd(BEHAVE_RUNNER_CONTAINER), prefix('source .env'):
    with cd(BEHAVE_RUNNER_CONTAINER):
        print(green('try unregister runner'))
        unregister_gitlab_runner(runner_name)

        print(green('register runner'))
        register_gitlab_runner(runner_name, android_api)


@task
def rebuild_gitlab():
    # # print(green('rebuild gitlabrunner base image'))
    # # run('docker build -t gitlabrunner:latest %s' % GITLAB_RUNNER_CONTAINER )
    # print(green('building gitlabrunner image'))
    # with cd(GITLAB_RUNNER_CONTAINER), quiet():
    #     run('docker build -t gitlabrunner .')

    # for the gitrunner token
    with cd(REMOTE_DIR), prefix('source .env'):
        print(green('putting all the things down'))
        run('docker-compose build')
        run('docker-compose down  --remove-orphans')

        rebuild_gitlab_container(GITLAB_NAME)

        # NOTE: the gitlab may not be wake up in time . so some sleep is required
        wait_for_gitlab_wakeup = 60
        print(yellow('wait a moment for gitlab up...%d seconds' % wait_for_gitlab_wakeup))
        time.sleep(wait_for_gitlab_wakeup)
        gitlab_check(GITLAB_SERVICE_NAME)


@task
def rebuild_runner():
    sync_files()
    with settings(warn_only=True):
        rebuild_runner_image()
        # rebuild_gitlab_shell_runner()
        # rebuild_beahve_runner('behave_runner_api22',['behave', 'android_api22'])
        # rebuild_beahve_runner('behave_runner_api23','android_api23', REG_TOKEN)
        # rebuild_beahve_runner('behave_runner_api24','android_api24', REG_TOKEN)
        rebuild_beahve_runner('behave_runner_api25', ['behave', 'android_api25'])


@task
def rebuild_reporter():
    try:
        sync_files()
        container = allure_report_container('allure_report')
        container.build_container()
    except Exception as e:
        raise e
    else:
        pass


@task
def rebuild_all():
    sync_files()
    rebuild_gitlab()
    rebuild_runner()
    rebuild_reporter()
