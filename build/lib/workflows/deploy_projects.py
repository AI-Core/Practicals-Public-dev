import os
import yaml
import json
import requests
import boto3
from prereqs_utils import Tree

def upload_directory_to_s3(source, bucketname, destination):
    for root, dirs, files in os.walk(source):
        for filename in files:
            local_path = os.path.join(root, filename)

            relative_path = os.path.relpath(local_path, source)
            s3_path = os.path.join(destination, relative_path)

            print(f"Searching {s3_path} in {bucketname}")
            try:
                s3.head_object(Bucket=bucketname, Key=s3_path)
                s3.delete_object(Bucket=bucketname, Key=s3_path)
            except:
                s3.upload_file(local_path, bucketname, s3_path)


def add_recursive_prerequisites_to_project(project_yaml, project_dir):
    recursive_prereqs_fp = os.path.join(
        "Projects/scenarios", project_dir, "task-to-recursive-prereqs.yaml"
    )
    if not os.path.exists(recursive_prereqs_fp):
        print(f"prereqs don't exist for project {project_dir}")
        return project_yaml
    with open(recursive_prereqs_fp) as f:
        tasks_to_recursive_prereqs = yaml.safe_load(f)

    for milestone in project_yaml["milestones"]:
        for task in milestone["tasks"]:
            # TODO use milestone and task client
            if "prerequisites" in task:
                task["prerequisites"] = tasks_to_recursive_prereqs[task["id"]]
    return project_yaml

if __name__ == '__main__':

    API_TOKEN = os.environ["API_TOKEN"]
    API_ROOT = os.environ["API_ROOT"]
    S3_BUCKET = os.environ["S3_BUCKET"]
    ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
    SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]

    fail_assert_flag = True

    s3 = boto3.client(
        "s3",
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
    )

    tree = Tree()
    print("Generating recursive prerequisites")
    tree.create_recursive_prerequisites()

    projects_failed_pathway = []
    projects_failed_bucket = []
    for project_folder in os.listdir("Projects/scenarios"):
        try:
            with open(f"Projects/scenarios/{project_folder}/specification.yaml") as file:
                project = yaml.safe_load(file)

            project = add_recursive_prerequisites_to_project(
                project, project_folder)

            project_id = project["id"]

            # Sends to API endpoint to be populated with ID etc.
            response = requests.post(
                f"{API_ROOT}/content/project",
                data=json.dumps(project),
                headers={"x-api-key": API_TOKEN},
            )
            print(response.json())
            print(response.status_code)
            assert (
                response.status_code == 200
            ), f"API response returned error code {response.status_code}"

        except:
            print("Unexpected error handling project. Continuing anyway.")
            fail_assert_flag = False
            projects_failed_pathway.append(project_folder)

        try:
            if os.path.isdir(f"Projects/scenarios/{project_folder}/repo"):
                print("Uploading template repo to s3")
                upload_directory_to_s3(
                    f"Projects/scenarios/{project_folder}/repo",
                    S3_BUCKET,
                    f"template-repos/{project_id}",
                )
        except:
            print("Unexpected error handling project repo template. Continuing anyway.")
            fail_assert_flag = False
            projects_failed_bucket.append(project_folder)

    assert fail_assert_flag, f"The following projects failed to deploy their pathway: {projects_failed_pathway} and the following projects failed to deploy their repo template: {projects_failed_bucket}"
