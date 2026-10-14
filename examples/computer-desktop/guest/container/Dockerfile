FROM mcr.microsoft.com/playwright/python@sha256:72bd171a9ffc2b4b59532aaa6210e21014d07093120dc25528870c0b840da1f0
RUN sed -i 's|http://azure.archive.ubuntu.com/ubuntu|https://archive.ubuntu.com/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources && apt-get -o APT::Update::Error-Mode=any update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends xdotool scrot mousepad openbox dbus-x11 x11-utils && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /opt/desktop /run/desktop /run/desktop-owner /home/desktop && \
    chown 1000:1000 /run/desktop /home/desktop && \
    printf '#!/bin/sh\nexec /ms-playwright/chromium-1243/chrome-linux64/chrome --class=chromium "$@"\n' > /usr/local/bin/chromium && \
    chmod 755 /usr/local/bin/chromium
COPY action.py start.py fixture.html bridge.py /opt/desktop/
USER 0:0
ENV HOME=/home/desktop DISPLAY=:1
CMD ["python3", "-I", "/opt/desktop/start.py"]
