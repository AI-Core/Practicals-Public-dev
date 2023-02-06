def create_instructions(
    image_1_path: str,
    image_2_path: str,
):
    md = (f'''
<details>
<summary>Some parts in this practical will require
you to create a new file. Click here to see how to do it.</summary>
<ul>
<li>Click on the folder logo on the left side of the screen</li>
<p align=center><img src="{image_1_path}"></p>
<li>Right click anywhere on the panel and click "New file"</li>
<p align=center><img src="{image_2_path}"></p>
</ul>
</details>
    ''')

    return md

def delete_instructions(
    image_1_path: str,
    image_2_path: str,
) -> str:
    md = (f'''
<details>
<summary>Some parts in this practical will require
you to delete a file. Click here to see how to do it.</summary>
<ul>
<li>Click on the folder logo on the left side of the screen</li>
<p align=center><img src="{image_1_path}"></p>
<li>Right click on the file you want to delete and click "Delete"</li>
<p align=center><img src="{image_2_path}"></p>
</ul>
</details>
    ''')

    return md

def read_instructions(
    image_1_path: str,
    image_2_path: str,
    image_3_path: str,
) -> str:
    md = (f'''
<details>
<summary>Some parts in this practical will require
you to open a file. Click here to see how to do it.</summary>
<ul>
<li>Click on the folder logo on the left side of the screen</li>
<p align=center><img src="{image_1_path}"></p>
<li>Double click on the file you want to open</li>
<p align=center><img src="{image_2_path}"></p>
<li>The file will appear on the right side of the screen</li>
<p align=center><img src="{image_3_path}"></p>
</ul>
</details>
    ''')

    return md

def update_instructions(
    image_1_path: str,
    image_2_path: str,
) -> str:
    md = (f'''
<details>
<summary>Some parts in this practical will require
you to update a file. Click here to see how to do it.</summary>
<ul>
<li>Click on the folder logo on the left side of the screen</li>
<p align=center><img src="{image_1_path}"></p>
<li>
    Double click on the file you want to update. The image will appear on the right side of the screen.
    You can edit the file by clicking on the text area, and then saving your changes.
</li>
<p align=center><img src="{image_2_path}"></p>
</ul>
</details>
    ''')

    return md

def upload_instructions(
    image_1_path: str,
    image_2_path: str,
) -> str:
    md = (f'''
<details>
<summary>Some parts in this practical will require
you to upload a file. Click here to see how to do it.</summary>
<ul>
<li>Click on the folder logo on the left side of the screen</li>
<p align=center><img src="{image_1_path}"></p>
<li>Click on the upload button on the top left corner</li>
<p align=center><img src="{image_2_path}"></p>
</ul>
</details>
    ''')

    return md

def run_instructions(
    image_1_path: str,
    image_2_path: str,
) -> str:
    md = (f'''
<details>
<summary>Some parts in this practical will require
you to run a code cell. Click here to see how to do it.</summary>
<ul>
<li>Check the name of the file you want to run</li>
<p align=center><img src="{image_1_path}"></p>
<li>In a cell, type <code>!python "name_of_the_file.py"</code></li>
<p align=center><img src="{image_2_path}"></p>
</ul>
</details>
    ''')

    return md
