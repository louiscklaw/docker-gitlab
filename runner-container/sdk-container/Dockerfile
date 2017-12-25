FROM ubuntu:14.04

RUN sed -i 's/http:\/\/archive\.ubuntu\.com/http:\/\/ftp\.cuhk\.edu\.hk\/pub\/Linux/g' /etc/apt/sources.list
RUN sed -i 's/http:\/\/security\.ubuntu\.com/http:\/\/ftp\.cuhk\.edu\.hk\/pub\/Linux/g' /etc/apt/sources.list

ENV DEBIAN_FRONTEND=noninteractive

#=============
# Set WORKDIR
#=============
WORKDIR /root

#==================
# General Packages
#------------------
# openjdk-8-jdk
#   Java
# ca-certificates
#   SSL client
# tzdata
#   Timezone
# unzip
#   Unzip zip file
# curl
#   Transfer data from or to a server
# wget
#   Network downloader
# libqt5webkit5
#   Web content engine (Fix issue in Android)
# libgconf-2-4
#   Required package for chrome and chromedriver to run on Linux
# xvfb
#   X virtual framebuffer
#==================


RUN apt-get -qqy update
RUN apt-get -qqy --no-install-recommends install apt-utils


# To add openjdk-8 on 14.04
RUN apt-get -qqy --no-install-recommends install software-properties-common
RUN add-apt-repository ppa:openjdk-r/ppa -y
RUN apt-get -qqy update


RUN apt-get -qqy --no-install-recommends install openjdk-8-jdk
RUN apt-get -qqy --no-install-recommends install ca-certificates
RUN apt-get -qqy --no-install-recommends install tzdata
RUN apt-get -qqy --no-install-recommends install unzip
RUN apt-get -qqy --no-install-recommends install curl
RUN apt-get -qqy --no-install-recommends install wget
RUN apt-get -qqy --no-install-recommends install libqt5webkit5
RUN apt-get -qqy --no-install-recommends install libgconf-2-4
RUN apt-get -qqy --no-install-recommends install xvfb
RUN rm -rf /var/lib/apt/lists/*

#===============
# Set JAVA_HOME
#===============
ENV JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/jre" \
    PATH=$PATH:$JAVA_HOME/bin

#=====================
# Install Android SDK
#=====================
ARG SDK_VERSION=sdk-tools-linux-3859397
ARG ANDROID_BUILD_TOOLS_VERSION=26.0.0
ENV SDK_VERSION=$SDK_VERSION \
    ANDROID_BUILD_TOOLS_VERSION=$ANDROID_BUILD_TOOLS_VERSION \
    ANDROID_HOME=/root

RUN wget -O tools.zip https://dl.google.com/android/repository/${SDK_VERSION}.zip
RUN unzip tools.zip && rm tools.zip
RUN chmod a+x -R $ANDROID_HOME
RUN chown -R root:root $ANDROID_HOME
ENV PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin

# https://askubuntu.com/questions/885658/android-sdk-repositories-cfg-could-not-be-loaded
RUN mkdir -p ~/.android
RUN touch ~/.android/repositories.cfg

RUN echo y | sdkmanager "platform-tools"
RUN echo y | sdkmanager "build-tools;$ANDROID_BUILD_TOOLS_VERSION"
ENV PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/build-tools

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y python python-pip python3 python3-pip

RUN pip3 install pipenv
