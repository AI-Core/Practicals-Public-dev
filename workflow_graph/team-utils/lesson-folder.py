import os


def list_files(startpath):
    body = ""
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        if level > 3:
            continue
        indent = ' ' * 4 * (level)
        body += f'\n{indent}{os.path.basename(root)}/'

    return body


with open("graph/team-utils/lesson-folder.txt", "w") as f:
    f.write(list_files("units"))
