from http import HTTPStatus

from flask import Blueprint, jsonify
import requests
import yaml
from prettytable.colortable import ColorTable, Themes

pipelines = Blueprint('pipeline', __name__)

@pipelines.route("/api/v1/pipelines", methods=['GET'])
def signup(table_format: str = 'text'):
    pipelines = []
    for project in get_config():

        for project_id in project['group_ids']:
            for pipeline_id in get_pipeline_ids(project_id, project['access-token']):
                group_name = project['project_name']
                pipelines.append(get_pipelines(group_name, project_id, pipeline_id, project['access-token']))

    columns = ["Student Name", "Class", "Subject", "Marks"]

    newTable = ColorTable(theme=Themes.OCEAN)
    newTable.field_names = ["Environment", "Project", "Repo", "Status", "Tag"]

    for blah in pipelines:
        newTable.add_row(
            [blah["env"],
             blah["group_name"],
             blah["project"],
             blah["status"] if blah["status"] != "manual" else '\033[31m' + blah["status"],
             blah["ref"]]
        )

    return newTable.get_formatted_string(table_format)

def client(path, token):
    url = 'https://gitlab.com/api/v4/{0}'.format(path)
    r = requests.get(url, headers={'PRIVATE-TOKEN': token})
    return r


def get_config():
    with open("piplines_config.yml") as f:
        try:
            content = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise FileNotFoundError(e)

    return content['gitlabs']


def get_project_repo_ids(project_id, token):
    r = client('groups/{0}/projects'.format(project_id), token)
    json = r.json()
    ids = []
    for name in json:
        if name['name'] in ['gitlab-config', 'infra', 'vault', 'grafana']:
            ids.append(name['id'])
    return ids

def get_project_name(project_id, token):
    r = client('projects/{0}'.format(project_id), token)
    json = r.json()
    name = [json['name']]
    return name[0]


def get_pipeline_ids(project_id, token):
    r = client('projects/{0}/pipeline_schedules/'.format(project_id), token)
    json = r.json()
    ids = []

    for id in json:
        ids.append(id['id'])
    return ids


def get_pipelines(group_name, project_id, pipeline_id, token):
    r = client('projects/{0}/pipeline_schedules/{1}'.format(project_id, pipeline_id), token)
    pipeline_json = r.json()
    # print(pipeline_json)
    pipelines = {"group_name": group_name,
                 "project": get_project_name(project_id, token),
                 "env": pipeline_json['description'],
                 "status": pipeline_json['last_pipeline']['status'],
                 "ref": pipeline_json['last_pipeline']['ref'],
                 "web_url": pipeline_json['last_pipeline']['web_url']}
    return pipelines
