# Use a compatible base image like Ubuntu or Debian
FROM --platform=linux/amd64 ubuntu:22.04
# Add necessary repositories for missing packages. Add the packages needed by K, and required at installation time.
RUN apt-get update && \
    apt-get install -y \
    software-properties-common \
    wget \
    gnupg \
    bash \
    python3 \
    python3-pip \
    build-essential \
    libusb-1.0-0-dev \
    libssl-dev \
    curl \
    nano \
    iputils-ping \
    gcc \
    git \
    jq \
    make \
    lsb-release \
    openjdk-17-jdk \
    libboost-dev \
    libboost-test-dev \
    libffi-dev \
    libfmt-dev \
    libgmp-dev \
    libjemalloc-dev \
    libmpfr-dev \
    libsecp256k1-0 \
    libtinfo-dev \
    libunwind-dev \
    libyaml-dev \
    libz3-4 \
    bison \
    flex \
    pkg-config \
    libcrypto++-dev \
    libsecp256k1-dev \
    cmake \
    maven \
    z3 \
    xxd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ARG HOME

# Pre-requisites

## Define build argument for GitHub Token

ARG GITHUB_TOKEN
ENV GITHUB_TOKEN=${GITHUB_TOKEN}

ARG KFRAMEWORK_REPO=github.com/runtimeverification/k.git
ARG K_COMMIT
ARG LLVM_VERSION=16
ARG GO_VERSION=1.23.1
ARG POETRY_VERSION=1.8.3

## Install LLVM 16: Install version 16 as later versions have a known bug affecting the code generator.

RUN wget https://apt.llvm.org/llvm.sh -O llvm.sh && chmod +x llvm.sh
RUN ./llvm.sh ${LLVM_VERSION} all && \
    apt-get install -y --no-install-recommends clang-${LLVM_VERSION} lldb-${LLVM_VERSION} lld-${LLVM_VERSION} && \
    rm -f llvm.sh

# Install Go

RUN wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz -O go${GO_VERSION}.linux-amd64.tar.gz
RUN rm -rf /usr/local/go && tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz && \
    rm go${GO_VERSION}.linux-amd64.tar.gz


ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g $GROUP_ID user && useradd -m -u $USER_ID -s /bin/sh -g user user

USER user:user
WORKDIR /home/user

## Setup the base directory
ENV WORKDIR=/home/user

# Add Go to the PATH
ENV PATH=$PATH:/usr/local/go/bin

## Install Poetry

RUN curl -sSL https://install.python-poetry.org -o install-poetry.py
RUN python3 install-poetry.py --version ${POETRY_VERSION} && rm install-poetry.py
ENV PATH=$HOME/.local/bin:$PATH

RUN pip3 install --user  \
           cytoolz       \
           numpy

# Install K
RUN git clone --depth=1 --branch v${K_COMMIT} https://${GITHUB_TOKEN}@${KFRAMEWORK_REPO} k
RUN cd k && git submodule update --init --recursive
ENV CXXFLAGS=-fvisibility=hidden
RUN cd k && mvn package -Dhaskell.backend.skip -DskipTests
ENV PATH=$WORKDIR/k/k-distribution/target/release/k/bin:$PATH

RUN mkdir /home/user/wasm-semantics
WORKDIR /home/user/wasm-semantics
