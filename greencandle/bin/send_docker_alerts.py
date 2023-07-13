#!/usr/bin/env python
#pylint: disable=no-member

"""
Check if docker containers are up/healthy, otherwise alert to slack
"""

import json
import requests_unixsocket
from greencandle.lib import config
from greencandle.lib.common import arg_decorator
from greencandle.lib.alerts import send_slack_message

config.create_config()

def get_docker_status(docker_socket):
    """
    Get docker status from socket file
    """
    session = requests_unixsocket.Session()
    container_list = []
    socket = docker_socket.replace("/", "%2F")
    url = f"http+unix://{socket}/containers/json?all=1"
    request = session.get(url)
    assert request.status_code == 200
    for container in json.loads(request.content):
        item = (container["Names"][0][0], container["Status"])
        if config.main.base_env in item:
            container_list.append(item)
    return container_list

@arg_decorator
def main():
    """
    Get Status of docker containers from docker socket file and send alerts for erroring containers.
    This script requires access to the socket file in /var/run/docker.sock, and config loaded into
    namespace so that alerts can be sent
    Errors will also be printed to STDOUT.
    This script is intended to be run from crontab.

    Usage: send_docker_alerts
    """


    issues = []
    docker_socket = "/var/run/docker.sock"
    container_list = get_docker_status(docker_socket)

    for item in container_list:
        name = item[0][0].lstrip('/')
        if any(status in item[1] for status in ["unhealthy", "Exited", "Restarting"]) and \
                "Exited (0)" not in item[1] and "k8s" not in name:
            issues.append(name)

    if issues:
        my_string = ', '.join(issues)
        send_slack_message("alerts", f"Issues with docker containers: {my_string}")

if __name__ == '__main__':
    main()
