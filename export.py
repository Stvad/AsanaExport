import argparse
import asana
from getpass import getpass
import json

from pathlib import Path

#compress name = asana-export-timestamp
#directory to save
#specific workspace
#specific project


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
            metadata_file.write(self.get_nice_json(workspace))

        projects = self.client.projects.find_by_workspace(workspace['id'], iterator_type=None, expand=["this"])
        for project in projects:
            self.process_project(workspace_path, project)

    def process_project(self, base_path, project):
        project_path = base_path.joinpath(project['name']+'.json')
        tasks = list(self.client.projects.tasks(project['id'], expand=["this", "subtasks+"]))
        project['tasks'] = tasks

        with project_path.open(mode='w', encoding='utf-8') as project_file:
            project_file.write(self.get_nice_json(project))


    @classmethod
    def get_nice_json(self, object): #move out from the class
        return json.dumps(object, sort_keys=True, indent=2, ensure_ascii=False)#.encode('utf-8')


if __name__ == '__main__':
    # token = getpass()
    # client = authorize(token)
    # print_data(client)

    parser = argparse.ArgumentParser(description='Export your data from Asana.')
    parser.add_argument('destination')
    args = parser.parse_args()

    asana_exporter = AsanaExporter()
    asana_exporter.export_data(args.destination)

    print("Exported successfully to: "+args.destination)

