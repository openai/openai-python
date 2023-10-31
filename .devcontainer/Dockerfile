# syntax=docker/dockerfile:1
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
  libxkbcommon0 \
  ca-certificates \
  make \
  curl \
  git \
  unzip \
  libc++1 \
  vim \
  termcap \
  && apt-get clean autoclean

RUN curl -sSf https://rye-up.com/get | RYE_VERSION="0.15.2" RYE_INSTALL_OPTION="--yes" bash
ENV PATH=/root/.rye/shims:$PATH

WORKDIR /workspace

COPY README.md .python-version pyproject.toml requirements.lock requirements-dev.lock /workspace/

RUN rye sync --all-features

COPY . /workspace

CMD ["rye", "shell"]
