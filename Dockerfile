FROM python:slim-buster

WORKDIR /

RUN /bin/sh -c set -eux;\
    apt-get update;\
    apt-get install -y jq curl
# install cldi
COPY --from=registry.devops.rivtower.com/cita-cloud/cloud-cli:latest /usr/bin/cldi /usr/local/bin/

# install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
RUN install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# install modules
RUN pip install tenacity
RUN pip install PyYaml

