FROM ubuntu:xenial

RUN sed -i 's/http:\/\/archive\.ubuntu\.com/http:\/\/ftp\.cuhk\.edu\.hk\/pub\/Linux/g' /etc/apt/sources.list
RUN sed -i 's/http:\/\/security\.ubuntu\.com/http:\/\/ftp\.cuhk\.edu\.hk\/pub\/Linux/g' /etc/apt/sources.list

#=============
# Set WORKDIR
#=============
ARG USER_DIR
ENV DEBIAN_FRONTEND="noninteractive"

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV SHELL=/bin/bash

RUN apt-get -qqy update && apt-get -qqy install --no-install-recommends \
    python python-pip python3 python3-pip python3-setuptools python-setuptools \
    git wget

RUN pip3 install pipenv && pip install pipenv

ADD config.toml /etc/gitlab-runner/config.toml

RUN wget -O /usr/local/bin/gitlab-runner https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64 &&\
    chmod +x /usr/local/bin/gitlab-runner &&\
    useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash &&\
    gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner




RUN apt-get -q clean -y && rm -rf /var/lib/apt/lists/* && rm -f /var/cache/apt/*.bin

# USER gitlab-runner

# CMD ["/usr/local/bin/gitlab-runner start"]
