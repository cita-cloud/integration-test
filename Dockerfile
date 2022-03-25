FROM debian:buster-slim

WORKDIR /

RUN /bin/sh -c set -eux;\
    apt-get update;\
    apt-get install -y jq;

# install cldi
COPY bin/cldi /usr/local/bin
RUN chmod +x /usr/local/bin/cldi

# install cco-cli
COPY bin/cco-cli /usr/local/bin
RUN chmod +x /usr/local/bin/cco-cli

COPY bin/kubectl /usr/local/bin
RUN chmod +x /usr/local/bin/kubectl
