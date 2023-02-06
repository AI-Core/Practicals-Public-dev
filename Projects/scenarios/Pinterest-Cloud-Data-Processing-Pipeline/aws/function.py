import boto3
import os
import cfnresponse
import json

sns_topic_arn = os.environ.get("SNS_TOPIC_ARN")
user_id = os.environ.get("USER_ID")
iam_user = os.environ.get("IAM_USER")
keypair_id = os.environ.get("KEYPAIR_ID")

sns = boto3.client("sns")


def lambda_handler(event, context):
    try:
        print("Event", event)
        request_type = event["RequestType"]
        if request_type == "Create":
            sns.publish(
                TopicArn=sns_topic_arn,
                Message=json.dumps(
                    {"userId": user_id, "iamUser": iam_user, "keyPairId": keypair_id}
                ),
            )
        else:
            print(f"RequestType {request_type} is not handled.")
        responseValue = 120
        responseData = {}
        responseData["Data"] = responseValue
        cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)
    except Exception as e:
        print("Error", e)
        responseData = {}
        responseData["Data"] = str(e)
        cfnresponse.send(event, context, cfnresponse.FAILED, responseData)
