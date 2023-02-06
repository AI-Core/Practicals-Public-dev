
import json
import glob
from pathlib import Path
import os
from pprint import pprint
from client import Content


def count_missing_videos():
    content = Content()
    lessons_with_missing_videos = [l for l in content.lessons if not l.video]
    pprint(lessons_with_missing_videos)
    print(len(lessons_with_missing_videos), "missing videos")


def count_missing_notebooks():
    content = Content()
    lessons_with_missing_notebooks = [
        l.path for l in content.lessons if not l.notebook]
    pprint(lessons_with_missing_notebooks)
    print(len(lessons_with_missing_notebooks), "missing notebooks")


def count_notebook_words():

    notebooks = Path('.').rglob('*Notebook.ipynb')

    wordCount = 0
    lines = 0
    num_notebooks = 0

    for notebook_fp in notebooks:
        num_notebooks += 1
        print(notebook_fp)

        with open(notebook_fp) as json_file:
            data = json.load(json_file)

        for each in data['cells']:
            cellType = each['cell_type']
            if cellType == "markdown":
                content = each['source']
                lines += len(content)
                for line in content:
                    # we might need to filter for more markdown keywords here
                    temp = [word for word in line.split() if "#" not in word]
                    wordCount = wordCount + len(temp)

    print(num_notebooks, 'notebooks')
    print(lines, 'lines')
    print(wordCount, 'words')
    print('words / 300:', wordCount / 300)


if __name__ == "__main__":
    count_missing_notebooks()
    count_missing_videos()
