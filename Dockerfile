FROM python:slim-bullseye

WORKDIR /

RUN apt-get update \
    && apt-get install -y --no-install-recommends crul mysql-client-5.7 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# install cldi
COPY --from=registry.devops.rivtower.com/cita-cloud/cloud-cli:latest /usr/bin/cldi /usr/local/bin/

# install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
RUN install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# install modules
RUN pip install tenacity PyYaml kubernetes pymysql
