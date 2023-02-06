import requests
import os
import json
from pprint import pprint


def create_or_update(_type, payload):
    _request("content", payload)


def set_prerequisites(module_id: str, prerequisite_module_ids: list):
    """Deletes existing prerequisites for module with id equal to `module_id` and assigns new ones equal to ids in `prerequisite_module_ids`"""
    _request("content/module/prerequisites", {
        'module_id': module_id,
        'prerequisite_module_ids': prerequisite_module_ids
    })


def _request(path, payload_yaml):

    API_ROOT = os.environ['API_ROOT']
    API_TOKEN = os.environ['API_TOKEN']

    print('----- path -----')
    print(path)
    print('----- payload_yaml -----')
    print(payload_yaml)

    url = f"{API_ROOT}/{path}"

    headers = {'x-api-key': f"{API_TOKEN}"}
    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(payload_yaml)
    )

    try:
        assert response.status_code == 200, f"{response.status_code} - {response.text}"
    except AssertionError as warning:
        print('\t\t\tAttempted payload:')
        pprint(payload_yaml)
        raise AssertionError(warning)
