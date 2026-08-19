ARG VARIANT="3.10"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

USER vscode

ADD --chmod=644 --checksum=sha256:504511fbbbd811aeaba6738abc79408956b6c7da0ca35437b3dcc24a41efc111 \
    https://github.com/astral-sh/uv/releases/download/0.12.5/uv-installer.sh /tmp/uv-installer.sh
RUN UV_NO_MODIFY_PATH=1 sh /tmp/uv-installer.sh
ENV PATH=/home/vscode/.local/bin:$PATH

RUN echo "[[ -d .venv ]] && source .venv/bin/activate || export PATH=\$PATH" >> /home/vscode/.bashrc
