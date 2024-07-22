ENV PATH=/home/vscode/.rye/shims:$PATH


RUN echo "[[ -d .venv ]] && source .venv/bin/activate" >> /home/vscode/.bashrc	RUN echo "[[ -d .venv ]] && source .venv/bin/activate" >> /home/vscode/.bashrc

#remove this pert
# Install PowerShell
RUN apt-get update && \
    apt-get install -y wget apt-transport-https software-properties-common && \
    wget -q "https://packages.microsoft.com/config/debian/10/packages-microsoft-prod.deb" && \
    dpkg -i packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y powershell
