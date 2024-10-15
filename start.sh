#!/bin/bash

# Checks if script name was provided; no entry runs client.py 
SCRIPT=${1:-client.py}

DISPLAY_NUM=99
VNC_PORT=5900

export DISPLAY=:$DISPLAY_NUM

echo "Starting with script: $SCRIPT"
echo "using DISPLAY :$DISPLAY_NUM"
echo "VNC Port: $VNC_PORT"

# Starts app based on entered value
if [ "$SCRIPT" == "server.py" ]; then
    echo "Starting server..."
    python server.py
else
# Start Xvfb
    echo "Starting Xvfb for client..."
    Xvfb :$DISPLAY_NUM -screen 0 570x400x24 &
    XVFB_PID=$!
    sleep 2

    if ! xdpyinfo -display :$DISPLAY_NUM >/dev/null 2>&1;
    then
      echo "xvfb failed to start"
      exit 1 
    fi

# Start VNC server
    echo "Starting VNC server..."
    x11vnc -display :$DISPLAY_NUM -forever -ncache 10 -nopw -listen 0.0.0.0 -xrandr -shared -verbose -rfbport $VNC_PORT &
    VNC_PID=$!
    sleep 2

    if ! ps -p $VNC_PID > /dev/null; 
    then
      echo "VNC server failed to start"
      exit 1
    fi

    echo "Starting client..."
    python client.py $SERVER_ADDR

    kill $XVFB_PID $VNC_PID
fi

