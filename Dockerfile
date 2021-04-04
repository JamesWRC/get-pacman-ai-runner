FROM docker.io/arm64v8/ubuntu:latest   
LABEL maintainer="github.com/JamesWRC"
ENV DEBIAN_FRONTEND=noninteractive

# Update system.
RUN apt -y update
RUN apt -y upgrade

# Prepare for Docker install
RUN apt -y install apt-transport-https ca-certificates curl gnupg2 lsb-release software-properties-common git
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
RUN echo \
  "deb [arch=arm64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null 

RUN apt update

# Install Docker
RUN apt -y install docker-ce docker-ce-cli containerd.io
RUN apt -y install sudo

# Environment requirements
RUN apt -y install python3-pip
RUN pip3 install psutil
COPY setupAndRun.py setupAndRun.py


CMD ["python3 setupAndRun.py"]

