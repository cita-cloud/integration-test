FROM python:slim-buster

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

# install schedule
RUN pip install schedule

