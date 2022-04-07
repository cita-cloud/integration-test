FROM debian:buster-slim

WORKDIR /

RUN /bin/sh -c set -eux;\
    apt-get update;\
    apt-get install -y jq curl
# install cldi
COPY --from=citacloud/cloud-cli:latest /usr/bin/cldi /usr/local/bin/

# install cco-cli
RUN curl -sLS https://raw.githubusercontent.com/cita-cloud/operator-proxy/master/install-cli.sh | bash

# install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
RUN install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# install python3.9
RUN apt upgrade -y &&\
    apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev -y &&\
    cd /tmp && wget https://www.python.org/ftp/python/3.9.7/Python-3.9.7.tgz &&\
    tar -xvf Python-3.9.7.tgz &&  cd Python-3.9.7/ && ./configure --enable-optimizations &&\
    make && make altinstall && \
    ln -s /usr/local/bin/python3.9 /usr/local/bin/python && \
    ln -s /usr/local/bin/pip3.9 /usr/local/bin/pip &&\
    pip install schedule

