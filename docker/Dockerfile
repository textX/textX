# From: https://github.com/liuchong/docker-rustup/blob/master/dockerfiles/stable/Dockerfile
FROM node:16-bullseye-slim as build

WORKDIR /root

# common packages
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    ca-certificates curl file \
    build-essential \
    autoconf automake autotools-dev libtool xutils-dev && \
    rm -rf /var/lib/apt/lists/*

ENV SSL_VERSION=1.0.2u

RUN curl https://www.openssl.org/source/openssl-$SSL_VERSION.tar.gz -O && \
    tar -xzf openssl-$SSL_VERSION.tar.gz && \
    cd openssl-$SSL_VERSION && ./config && make depend && make install && \
    cd .. && rm -rf openssl-$SSL_VERSION*

ENV OPENSSL_LIB_DIR=/usr/local/ssl/lib \
    OPENSSL_INCLUDE_DIR=/usr/local/ssl/include \
    OPENSSL_STATIC=1

# install toolchain
RUN curl https://sh.rustup.rs -sSf | \
    sh -s -- --default-toolchain stable -y

ENV PATH=/root/.cargo/bin:$PATH

# Install mdbook and processors
ENV MDBOOK=0.4.37
ENV MDBOOK_ADMONISH=1.15.0
ENV MDBOOK_THEME=0.1.4
ENV MDBOOK_BIB=0.0.6
ENV MDBOOK_LINKCHECK=0.7.7

RUN cargo install --version $MDBOOK mdbook
RUN cargo install --version $MDBOOK_ADMONISH mdbook-admonish
RUN cargo install --version $MDBOOK_THEME mdbook-theme
RUN cargo install --version $MDBOOK_LINKCHECK mdbook-linkcheck
RUN cargo install --version $MDBOOK_BIB mdbook-bib

FROM node:16-bullseye-slim
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*
COPY --from=build /root/.cargo/* /bin/
VOLUME /p
WORKDIR /p
EXPOSE 3000
