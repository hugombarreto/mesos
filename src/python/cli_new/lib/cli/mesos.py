# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Functions to handle agents.
"""

from cli import http
from cli.exceptions import CLIException


def get_agent_address(agent_id, master):
    """
    Given a master and an agent id, return the agent address
    by checking the /slaves endpoint of the master.
    """
    try:
        agents = http.get_json(master, "slaves")["slaves"]
    except Exception as exception:
        raise CLIException("Could not open '/slaves'"
                           " endpoint at '{addr}': {error}"
                           .format(addr=master,
                                   error=exception))
    for agent in agents:
        if agent["id"] == agent_id:
            return agent["pid"].split("@")[1]
    raise CLIException("Unable to find agent '{id}'".format(id=agent_id))


def get_agents(master):
    """
    Get the agents in a Mesos cluster.
    """
    endpoint = "slaves"
    key = "slaves"

    try:
        data = http.get_json(master, endpoint)
    except Exception as exception:
        raise CLIException(
            "Could not open '/{endpoint}' on master: {error}"
            .format(endpoint=endpoint, error=exception))

    if not key in data:
        raise CLIException(
            "Missing '{key}' key in data retrieved"
            " from master on '/{endpoint}'"
            .format(key=key, endpoint=endpoint))

    return data[key]


def get_container_id(task):
    """
    Get the container ID of a task.
    """

    if 'statuses' not in task:
        raise CLIException("Unable to obtain status information for task")

    statuses = task['statuses']
    if not statuses:
        raise CLIException("No status updates available for task")

    # It doesn't matter which status we use to get the `container_id`, if the
    # `container_id` has been set for the task, all statuses will contain it.
    if not 'container_status' in statuses[0]:
        raise CLIException("Task status does not contain container information")

    container_status = statuses[0]['container_status']
    if 'container_id' in container_status:
        container_id = container_status['container_id']
        if 'value' in container_id:
            return container_id

    raise CLIException(
        "No container found for the specified task."
        " It might still be spinning up."
        " Please try again.")


def get_tasks(master):
    """
    Get the tasks in a Mesos cluster.
    """
    endpoint = "tasks"
    key = "tasks"

    try:
        data = http.get_json(master, endpoint)
    except Exception as exception:
        raise CLIException(
            "Could not open '/{endpoint}' on master: {error}"
            .format(endpoint=endpoint, error=exception))

    if not key in data:
        raise CLIException(
            "Missing '{key}' key in data retrieved"
            " from master on '/{endpoint}'"
            .format(key=key, endpoint=endpoint))

    return data[key]