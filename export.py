import argparse
import asana
import os
from getpass import getpass
from pprint import pprint
import json

#compress name = asana-export-timestamp
#directory to save
#specific workspace
#specific project
import sys


def authorize(token):
    return asana.Client.access_token(token)

def print_data(client):
    workspaces = list(client.workspaces.find_all(expand=["this"]))
    for workspace in workspaces:
        print(workspace)

    # print(workspaces[0])
    # print(workspaces[0]['id'])
    #projects = client.projects.find_by_workspace(workspaces[0]['id'], iterator_type=None)
    projects = client.projects.find_by_workspace(57094690913001, iterator_type=None, expand=["this"]) #personal_projects and tasks
    #for project in projects:
    #    print(project)

    # pprint(projects[0])
    # print(json.dumps(projects[0], sort_keys=True, indent=2, separators=(',', ': ')))
    working_project = projects[0]
    tasks_exp = list(client.projects.tasks(working_project['id'], expand=["this", "subtasks+"]))#params={"pretty": True, "expand": "[\"this\", \"subtasks\"]"})
    # pprint(list(tasks_exp)[0])

    working_project['testtask'] = tasks_exp

    with open(working_project['name'], 'w', encoding="utf-8") as projectfile:
        projectfile.write(json.dumps(working_project, sort_keys=True, indent=2, separators=(',', ': ')))



    # tasks = client.tasks.find_by_project(projects[0]['id'])
    # for task in tasks:
    #     print(task)

def export_data(destination):

    auth_token = getpass
    client = authorize(auth_token)

    os.makedirs()


if __name__ == '__main__':
    token = getpass()
    client = authorize(token)
    print_data(client)

    parser = argparse.ArgumentParser(description='Export your data from Asana.')
    parser.add_argument('destination')
    args = parser.parse_args()

