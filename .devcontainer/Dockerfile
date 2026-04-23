ARG VARIANT="3.9"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}
COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /usr/local/bin/uv

USER vscode

RUN echo "[[ -d .venv ]] && source .venv/bin/activate || export PATH=\$PATH" >> /home/vscode/.bashrc
