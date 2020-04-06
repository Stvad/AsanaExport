#!/usr/bin/env python

import argparse
import asana
import json
import os
import sys

from getpass import getpass
from pathlib import Path


class AsanaAuthorizationUtil:

    @staticmethod
    def authorize():
        client = None
        if 'ASANA_CLIENT_ID' in os.environ:
            # create a client with the OAuth credentials:
            client = asana.Client.oauth(
                client_id=os.environ['ASANA_CLIENT_ID'],
                client_secret=os.environ['ASANA_CLIENT_SECRET'],
                # this special redirect URI will prompt the user to copy/paste the code.
                # useful for command line scripts and other non-web apps
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )

            # get an authorization URL:
            (url, state) = client.session.authorization_url()
            try:
                import webbrowser
                webbrowser.open(url)
            except Exception as e:
                print("Open the following URL in a browser to authorize:")
                print(url)

            print("Copy and paste the returned code from the browser and press enter:")

            code = sys.stdin.readline().strip()
            # exchange the code for a bearer token
            client.session.fetch_token(code=code)  # Todo: consider saving and reusing the token

        else:
            print("Enter your personal access token:")
            auth_token = getpass()
            client = asana.Client.access_token(auth_token)

        return client


def get_nice_json(object_to_dump):
    return json.dumps(object_to_dump, sort_keys=True, indent=2, ensure_ascii=False)


class AsanaExporter:
    def __init__(self):
        self.destination_path = None
        self.client = None

    def export_data(self, destination):

        self.destination_path = Path(destination)

        self.client = AsanaAuthorizationUtil.authorize()

        workspaces = list(self.client.workspaces.find_all(expand=["this"]))
        for workspace in workspaces:
            self.process_workspace(workspace)

    def process_workspace(self, workspace):
        workspace_path = self.destination_path.joinpath(workspace['name'])
        workspace_path.mkdir(parents=True, exist_ok=True)

        metadata_path = workspace_path.joinpath('workspace_information.json')
        with metadata_path.open(mode='w', encoding='utf-8') as metadata_file:
            metadata_file.write(get_nice_json(workspace))

        print("Exporting workspace:", workspace)
        projects = self.client.projects.find_by_workspace(workspace['gid'], iterator_type=None, expand=["this"])
        for project in projects:
            self.process_project(workspace_path, project)

    def process_project(self, base_path, project):
        print("Exporting project:", project)
        project_path = base_path.joinpath(project['name'] + '.json')
        tasks = list(self.client.projects.tasks(project['gid'], expand=["this", "subtasks+"]))
        project['tasks'] = tasks

        with project_path.open(mode='w', encoding='utf-8') as project_file:
            project_file.write(get_nice_json(project))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export your data from Asana.')
    parser.add_argument('destination')
    args = parser.parse_args()

    asana_exporter = AsanaExporter()
    asana_exporter.export_data(args.destination)

    print("Exported successfully to: " + args.destination)
