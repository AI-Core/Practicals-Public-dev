from utils.client import Content
from utils.client import Practical
from typing import List
import nbformat
import glob
import os
import boto3
import shutil
from utils.instructions_images.instructions_dict import instructions_dict

def add_libraries_to_notebook(
    practical: Practical,
) -> None:
    """
    Adds a cell to the top of the notebook to install the libraries

    Parameters
    ----------
    practical: Practical
        The practical with the notebook to add the cell to
    libraries: List[str]
        The libraries to install
    """
    string_to_add = ""
    has_string = False

    # Adds requirements to the notebook
    requirements_file = os.path.join(
        os.path.dirname(practical.practical_notebook_path),
        "requirements.txt"
    )
    if os.path.exists(requirements_file):
        libraries = add_requirement_installation(
            requirements_path=requirements_file,
            has_string=has_string,
        )
        string_to_add += libraries
        has_string = True

    # Downloads and import files
    imports_folder = os.path.join(
        os.path.dirname(practical.practical_notebook_path),
        "Imports"
    )
    if os.path.exists(imports_folder):
        imports = add_files_to_s3_and_get_code(
            attachment_folder=imports_folder,
            practical_id=practical.id,
            s3=s3,
            imports=True,
            has_string=has_string,
        )
        string_to_add += imports
        has_string = True

    # Downloads files
    attachments_folder = os.path.join(
        os.path.dirname(practical.practical_notebook_path),
        "Attachments"
    )
    if os.path.exists(attachments_folder):
        attachments = add_files_to_s3_and_get_code(
            attachment_folder=attachments_folder,
            practical_id=practical.id,
            s3=s3,
            has_string=has_string,
        )
        string_to_add += attachments

    # Downloads zip files and unzips them
    zip_folder = os.path.join(
        os.path.dirname(practical.practical_notebook_path),
        "Compressed"
    )
    if os.path.exists(zip_folder):
        zip_files = add_files_to_s3_and_get_code(
            attachment_folder=zip_folder,
            practical_id=practical.id,
            s3=s3,
            is_zip=True,
            has_string=has_string,
        )
        string_to_add += zip_files
        has_string = True

    if len(string_to_add) == 0:
        return False

    with open(practical.practical_notebook_path, "r") as f:
        nb = nbformat.read(f, as_version=4)

    new_cell = nbformat.v4.new_code_cell(string_to_add)
    nb.cells.insert(1, new_cell)

    with open(practical.practical_notebook_path, "w") as f:
        nbformat.write(nb, f)

    return True

def add_files_to_s3_and_get_code(
    attachment_folder: str,
    practical_id: str,
    s3: boto3.client,
    imports: bool = False,
    is_zip: bool = False,
    has_string: bool = False,
) -> None:
    """
    Saves a file to S3 and adds a cell to the top of the notebook to download the file
    and import the module

    Parameters
    ----------
    practical: Practical
        The practical with the notebook to add the cell to
    imports_folder: str
        The folder containing the files to upload
    s3: boto3.client
        The boto3 client to upload the files to S3
    """
    files_within_folder = glob.glob(f"{attachment_folder}/*")

    string_for_cell = ""
    if not has_string:
        string_for_cell = (
            '#@title # Run the following cell to download the necessary files for this practical.'
            ' { display-mode: "form" } \n'
            "#@markdown Don't worry about what's in this collapsed cell\n\n"
        )

    for file in files_within_folder:
        file_name = os.path.basename(file)
        print(f"Uploading {file_name} to 'practicals_files/{practical_id}/{file_name}'")
        s3.upload_file(file, S3_BUCKET, f"practicals_files/{practical_id}/{file_name}")

        print(f"Adding wget command to {practical.practical_notebook_path}")

        # Add a cell at the top of the notebook
        string_for_cell += (
            f"print('Downloading {file_name}...')\n"
            f"!wget https://s3-eu-west-1.amazonaws.com/{S3_BUCKET}/practicals_files/{practical_id}/{file_name} -q\n"
        )
        if is_zip:
            string_for_cell += f"!unzip {file_name} > /dev/null\n"
            string_for_cell += f"!rm {file_name}\n"
        if imports:
            # Remove extension to file
            import_name = file_name.split(".")[0]
            string_for_cell += f"import {import_name}\n"
    return string_for_cell

def add_requirement_installation(
    requirements_path: str,
    has_string: bool = False,
) -> None:
    """
    Adds a cell to the top of the notebook to install the libraries

    Parameters
    ----------
    practical: Practical
        The practical with the notebook to add the cell to
    string_for_cell: str
        The string to add to the cell. If empty, a default string will be used
    """
    string_for_cell = ""
    if not has_string:
        string_for_cell = (
            '#@title # Run the following cell to install the necessary libraries for this practical.'
            ' { display-mode: "form" } \n'
            "#@markdown Don't worry about what's in this collapsed cell\n\n"
        )

    with open(requirements_path, "r") as f:
        requirements = f.read().splitlines()
    for requirement in requirements:
        string_for_cell += f"!pip install -q {requirement}\n"
    return string_for_cell

def add_instructions_to_notebook(
    practical: Practical,
    added_downloads: bool,
):
    instructions = practical.instructions
    if instructions is None:
        return
    # Add the create images to the notebook path

    instruction_text = ""
    for instruction in instructions:
        if instruction in instructions_dict.keys():
            images_paths = instructions_dict[instruction]['images']
            images_paths_dict = {}
            for n, image_path in enumerate(images_paths, 1):
                end_path = f"images/{instruction}_{n}.png"
                images_paths_dict[f"image_{n}_path"] = end_path
                target_path = os.path.join(
                    os.path.dirname(practical.practical_notebook_path),
                    end_path
                )
                target_path_folder = os.path.dirname(target_path)
                if not os.path.exists(target_path_folder):
                    os.makedirs(target_path_folder, exist_ok=True)

                shutil.copyfile(
                    image_path,
                    os.path.join(
                        os.path.dirname(practical.practical_notebook_path),
                        end_path,
                    ),
                )
            instruction_text += instructions_dict[instruction]['instructions'](**images_paths_dict)

    with open(practical.practical_notebook_path, "r") as f:
        nb = nbformat.read(f, as_version=4)

    new_cell = nbformat.v4.new_markdown_cell(instruction_text)
    if added_downloads:
        nb.cells.insert(2, new_cell)
    else:
        nb.cells.insert(1, new_cell)

    with open(practical.practical_notebook_path, "w") as f:
        nbformat.write(nb, f)

if __name__ == "__main__":

    API_TOKEN = os.environ["API_TOKEN"]
    API_ROOT = os.environ["API_ROOT"]
    S3_BUCKET = os.environ["S3_PUBLIC_BUCKET"]
    ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
    SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
    s3 = boto3.client(
        "s3",
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
    )
    content = Content()
    lessons = content.lessons
    practicals: List[Practical] = [practical for lesson in lessons for practical in lesson.practicals]
    practicals_with_nb = [practical for practical in practicals if practical.practical_notebook_path]

    # Upload files for those practicals with a `files` folder in the same directory
    for practical in practicals_with_nb:
        added_downloads = add_libraries_to_notebook(practical)
        if practical.instructions:
            add_instructions_to_notebook(
                practical,
                added_downloads,
            )
