#!/usr/bin/env python

import argparse
import asana
from getpass import getpass
import json

from pathlib import Path


def authorize(token):
    return asana.Client.access_token(token)


def get_nice_json(object_to_dump):
        return json.dumps(object_to_dump, sort_keys=True, indent=2, ensure_ascii=False)


class AsanaExporter:
    def __init__(self):
        self.destination_path = None
        self.client = None

    def export_data(self, destination):

        self.destination_path = Path(destination)

        auth_token = getpass()
        self.client = authorize(auth_token)

        workspaces = list(self.client.workspaces.find_all(expand=["this"]))
        for workspace in workspaces:
            self.process_workspace(workspace)

    def process_workspace(self, workspace):
        workspace_path = self.destination_path.joinpath(workspace['name'])
        workspace_path.mkdir(parents=True, exist_ok=True)

        metadata_path = workspace_path.joinpath('workspace_information.json')
        with metadata_path.open(mode='w', encoding='utf-8') as metadata_file:
            metadata_file.write(get_nice_json(workspace))

        projects = self.client.projects.find_by_workspace(workspace['id'], iterator_type=None, expand=["this"])
        for project in projects:
            self.process_project(workspace_path, project)

    def process_project(self, base_path, project):
        project_path = base_path.joinpath(project['name']+'.json')
        tasks = list(self.client.projects.tasks(project['id'], expand=["this", "subtasks+"]))
        project['tasks'] = tasks

        with project_path.open(mode='w', encoding='utf-8') as project_file:
            project_file.write(get_nice_json(project))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Export your data from Asana.')
    parser.add_argument('destination')
    args = parser.parse_args()

    asana_exporter = AsanaExporter()
    asana_exporter.export_data(args.destination)

    print("Exported successfully to: "+args.destination)

