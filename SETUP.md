## Steps for running app:

    I used Docker and docker-compose to containerize this project. The docker-compose.yml file creates a server container and a client container, the server container outputs to stdout while the client container utilizes a VNC server to view the GUI on a host machine. 

## To start the containers: 

    run docker compose up --build, if you want to test multiple clients connecting to the server run: docker compose up --scale:2 (after running the first command) The vnc server only works if you --build the containers each time as sequential client containers need to have their ports recalculated (from start.sh)
    
    Once the containers are up you should be able to view the logs and port numbers of the server and client(s).

    the server will output messages received from the client container to its logs (stdout). If you want to view the output in your own terminal run: docker attach project-1-server-1, when a message is received it will display in your terminal's stdout.

## To view the client's GUI: 

    The client container(s) use a VNC server to display the GUI. To view the GUI you will need a VNC viewer like xtigervncviewer. Once you have the VNCviewer up and running, check your docker containers (using docker ps or looking on the desktop app) for the port number assigned. In the vncviewer enter 0.0.0.0:<port number> into the ip address box and hit 'connect' you should now be able to view the GUI. 

## Steps for running standalone containers: 

    if you dont want to use docker compose for some reason, the below steps will allow you to start standalone containers running client.py and server.py 

    both client.py and server.py use the same dockerfile. to run server.py in the container you need to append server.py to the end of the docker run command, if no argument is input, the dockerfile will default to running client.py

    To run client: docker build -t <name> . (I used the name kylertk21/net-app for the image and the container)
                   docker run -p 5900:5900 <name>

    The dockerfile has instructions to install and deploy a vnc server to display the client GUI

    On the host machine start a vncviewer (I used xtigervncviewer, but most vncviewers should work)

    xtigervncviewer can be downloaded from http://tigervnc.bphinz.com/nightly/ (scroll to the bottom for windows installers)

    in the ip-address box, type '0.0.0.0:5900', you should now see the GUI

    To run the server: docker build -t <name> . 
                       docker run -it -p 4321:4321/udp <name> server.py


