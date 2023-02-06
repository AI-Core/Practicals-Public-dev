from utils.client import Pathways
import requests
import json
import os
import boto3
import yaml

if __name__ == '__main__':
    API_TOKEN = os.environ["API_TOKEN"]
    API_ROOT = os.environ["API_ROOT"]
    membership_key_path = "Pathways/membership_keys.yaml"
    with open(membership_key_path, 'r') as f:
        membership_keys = yaml.safe_load(f)

    pathways = Pathways()
    pathways.validate()
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )
    for pathway in pathways:
        print(f"Deploying {pathway.name}...\n")
        payload = pathway.payload
        membership_key_pathway = []
        for membership_key in membership_keys:
            membership_keys_pathway_ids = [pathway["id"] for pathway in membership_key["pathways"]]
            if pathway.id in membership_keys_pathway_ids:
                membership_key_pathway.append(membership_key["name"])
        payload["membership_keys"] = membership_key_pathway
        response = requests.post(
            f"{API_ROOT}/content/pathway",
            data=json.dumps(payload),
            headers={"x-api-key": API_TOKEN},
        )
        if response.status_code != 200:
            print(f'Something went wrong with the pathway: {pathway.name}')
            print(response.json())
        if pathway.cover_img:
            pathway_id = pathway.id
            path_to_upload = pathway.cover_img_path
            s3.upload_file(
                path_to_upload,
                os.environ["S3_PUBLIC_BUCKET"],
                f"cover-images/Pathways/{pathway_id}.png",
            )
