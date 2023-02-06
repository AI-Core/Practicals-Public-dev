'''
Validates and deploy unlockables to the API

The unlockables are located in any directory that contains a unlockables.yaml file.

It's important to define the content_type of the unlockable, as this will determine the type_id of the unlockable.
The specs for the projects are in the specifcation.yaml file.
But for units, modules, and lessons the specs have the same name as
the content_type (unit.yaml, module.yaml, lesson.yaml)

If the content_type is a task, the spec should include the uuid of the task

This script contains both deployment and validation functions.
'''
import os
import yaml
import json
import requests
import glob
from typing import List


def read_metadata(
    path: str,
    content_type: str
) -> str:
    '''
    Reads the metadata for the unlockable from the appropriate file

    Parameters
    ----------
    path : str
        The path to the unlockables.yaml file
    content_type : str
        The content_type of the unlockable
    '''
    meta_path = path.replace("unlockables.yaml", f"{content_type}.yaml")
    with open(meta_path, "r") as f:
        metadata = yaml.safe_load(f)
        meta_id = metadata["id"]
    return meta_id

def check_keys(
    unlockable: dict,
    necessary_keys: List[str],
    optional_keys: List[str],
    path: str = None
) -> None:
    '''
    Checks that all the necessary keys are present in the unlockable

    Parameters
    ----------
    unlockable : dict
        The unlockable to check
    necessary_keys : list
        The list of necessary keys

    Raises
    ------
    AssertionError
        If a necessary key is missing
    '''
    for key in necessary_keys:
        if "name" in unlockable.keys():
            assert key in unlockable, f"{key} is missing from {unlockable['name']} in {'/'.join(path.split('/')[-3:])}"
        else:
            assert key in unlockable, f"{key} is missing from {path}"

    for key in optional_keys:
        if key not in unlockable.keys():
            if key == "is_active":
                unlockable["is_active"] = True
            else:
                unlockable[key] = None

def set_type_id(
    unlockable: dict,
    path: str
) -> dict:
    '''
    Sets the type_id of the unlockable

    Parameters
    ----------
    unlockable : dict
        The unlockable to set the type_id for
    content_type : str
        The content_type of the unlockable
    path : str
        The path to the unlockables.yaml file

    Returns
    -------
    unlockable : dict
        The unlockable with the type_id set
    '''
    content_type = unlockable["content_type"]
    # The content_type of the unlockable determines the type_id
    if content_type == 'project':
        project_id = read_metadata(path, "specification")
        unlockable["type_id"] = project_id
    elif content_type != 'task':
        meta_id = read_metadata(path, content_type)
        unlockable["type_id"] = meta_id
    elif content_type == 'task':
        assert "task_id" in unlockable, \
            "If the content_type is a task, the unlockable must include the task_id"
        unlockable["type_id"] = unlockable.pop("task_id")
    return unlockable


if __name__ == "__main__":
    API_TOKEN = os.environ["API_TOKEN"]
    API_ROOT = os.environ["API_ROOT"]

    project_unlockable_keys = [
        "id",
        "unlockable_id",
        "content_type",
        "type_id"
    ]

    unlockable_keys = [
        "name",
        "unlockable_id",
        "unlockable_type",
        "description",
        "prerequisites",
        "template_url",
        "due_date",
        "is_active",
    ]

    necessary_keys = [
        "id",
        "name",
        "unlockable_id",
        "unlockable_type",
        "description",
        "content_type",
    ]

    optional_keys = [
        "prerequisites",
        "template_url",
        "due_date",
        "is_active",
    ]
    # Some unlockables don't need a type_id (e.g. tasks)

    unlockables = glob.glob("**/unlockables.yaml", recursive=True)
    unlockable_list = []
    for unlockable_path in unlockables:
        with open(unlockable_path, "r") as f:
            data: List[dict] = yaml.safe_load(f)
            project_unlockable_list = []
            for unlockable in data:
                # Check that all the necessary keys are present
                check_keys(
                    unlockable,
                    necessary_keys,
                    optional_keys,
                    unlockable_path
                )
                unlockable = set_type_id(unlockable, unlockable_path)

                project_unlockable = {k: unlockable[k] for k in project_unlockable_keys}
                project_unlockable['type'] = project_unlockable.pop('content_type')
                project_unlockable_list.append(project_unlockable)

                unlockable = {k: unlockable[k] for k in unlockable_keys}
                # Rename some keys to adapt the payload to the API
                unlockable['id'] = unlockable.pop('unlockable_id')
                unlockable['type'] = unlockable.pop('unlockable_type')
                unlockable_list.append(unlockable)
            print(f"Deploying unlockables for {unlockable_path}")
            response = requests.post(
                f"{API_ROOT}/content/project-unlockables",
                headers={"x-api-key": API_TOKEN},
                data=json.dumps(project_unlockable_list)
            )
            assert response.status_code == 200, f"Failed to deploy project unlockables: {response.text}"
    print("Successfully deployed project unlockables")

    print("Deploying unlockables")
    response = requests.post(
        f"{API_ROOT}/content/unlockables",
        headers={"x-api-key": API_TOKEN},
        data=json.dumps(unlockable_list)
    )
    assert response.status_code == 200, f"Failed to deploy unlockables: {response.text}"
    print("Successfully deployed unlockables")
