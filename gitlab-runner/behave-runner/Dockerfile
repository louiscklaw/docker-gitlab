FROM gitlabrunner:latest

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y python python-pip python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install pipenv
