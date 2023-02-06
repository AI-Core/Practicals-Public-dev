from utils.client import Content  # noqa: E402
import boto3
import os

if __name__ == "__main__":
    content = Content()
    content.create_or_update()

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )
    for lesson in content.lessons:
        if lesson.cover_img:
            lesson_id = lesson.id
            path_to_upload = lesson.cover_img_path
            s3.upload_file(
                path_to_upload,
                os.environ["S3_PUBLIC_BUCKET"],
                f"cover-images/Lessons/{lesson_id}.png",
            )
