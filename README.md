# drone-phone-cloudapi
mock a drone with your phone to a cloudapi that does mqtt for location and webrtc for the camera

TLDR;

1. Follow the instructions here to bootstrap ansible-pull and code-server
2. Use `/opt/ansible_env/bin/ansible-pull -U https://github.com/rhildred/drone-phone-cloudapi.git` to pull caddy, caddy-ask-api, mosquitto, and mediamtx.
3. Edit the Caddyfile and the domains.json file in /etc/caddy so that you can bring up your code-server instance from step 1.

At this point this is a terminal with code-server. There are still configuration tasks for mosquitto and mediamtx but these can be done when setting up the actual workings of the system.
