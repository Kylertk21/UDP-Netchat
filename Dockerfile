
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
  python3-tk \
  inetutils-ping \
  iproute2 \
  x11-apps \
  x11vnc \
  xvfb \
  net-tools \
  procps \
  fluxbox \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY /src /app

EXPOSE 4321
EXPOSE 5900

ENV DISPLAY=:99
ENV RESOLUTION=570x400x24

COPY start.sh /start.sh
RUN chmod +x /start.sh


