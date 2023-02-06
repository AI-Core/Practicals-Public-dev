import os
import yaml
import urllib
from utils import api
import uuid
import collections
from glob import glob
import nbformat
import string
from typing import List, Union, Optional
import warnings
warnings.filterwarnings('ignore')

S3_PUBLIC_BUCKET = os.environ.get("S3_PUBLIC_BUCKET")

def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))

        return True
    except ValueError:
        raise ValueError(f"{value} is an invalid UUID")

def dev_assert(condition, message, additional=None):
    '''
    Regular assertion but if it's on dev, it just prints the message
    If the condition is not met in dev, it applies some `additional` changes 
    so the validation keeps runnin
    '''
    # TODO: There are way too many things to correct in the notebooks. 
    # They will be visible in the validation.log file
    # After correcting all of them, comment back in the following lines

    # if os.environ.get('Stage') == 'STAGING' or os.environ.get('Stage') == 'PROD':
    #     assert condition, message
    # elif not condition:
    #     with open('validation.log', 'a') as f:
    #         f.write(message + "\n")
    #     if additional:
    #         return additional

    # TODO: And then remove the following lines

    if not condition:
        with open('validation.log', 'a') as f:
            f.write(message + "\n")
        if additional:
            return additional

# Added at the beginning for dependency injection

words_to_not_capitalise = [
    "the", "a", "an", "and", "as", "as", "if", "as", "long", "as", "at", "but", "by", "even", "for", "from", "only",
    "in", "into", "like", "near", "now", "that", "nor", "of", "off", "on", "on", "top", "once", "onto", "or", "out",
    "of", "over", "past", "so", "so", "that", "than", "that", "till", "to", "up", "upon", "with", "when", "yet"
]

class Content:
    def __init__(self):
        self.units = Units()
        self.modules = []
        self.lessons = []
        for unit in self.units:
            for module in unit.modules:
                self.modules.append(module)
                for lesson in module.lessons:
                    self.lessons.append(lesson)

    def validate(self):
        # Create a file to store the validation log
        if os.environ.get('Stage') == 'DEV':
            with open('validation.log', 'w') as f:
                f.write('')
        for unit in self.units:
            unit.validate()

            for module in unit.modules:
                module.validate()

                for lesson in module.lessons:
                    lesson.validate()

        validate_ids_are_unique(self.get_ids())

    def create_or_update(self):
        for unit in self.units:

            print(f'Updating unit {unit}')
            unit.create_or_update()

    def get_ids(self):
        return [
            *[u.id for u in self.units],
            *[m.id for m in self.modules],
            *[l.id for l in self.lessons]
        ]

    def get_lesson_from_id(self, id):
        try:
            return [
                l for l in self.lessons if l.id == id][0]
        except IndexError as e:
            raise IndexError(f'The lesson with ID {id} could not be found')

    def get_id_from_lesson_name(
        self,
        lesson
    ) -> Optional[str]:
        try:
            return [
                l.id for l in self.lessons if l.name == lesson][0]
        except IndexError as e:
            return None

    def get_recursive_prerequisites(self,
                                    lesson: 'Lesson',
                                    level: int = 0,
                                    source_lesson: Union['Lesson',
                                                         List['Lesson'],
                                                         None] = None):
        '''
        Returns a list of all prerequisites for a lesson, including prerequisites of prerequisites

        Parameters
        ----------
        lesson : Lesson
            The lesson to get the prerequisites for
        level : int
            The current level of recursion
        '''
        # in the first level of the call, all of the direct prereqs are put first
        if source_lesson and isinstance(source_lesson, Lesson):
            source_lesson = [source_lesson]

        if source_lesson and (lesson in source_lesson):
            return [], level

        recursive_prerequisites = []
        prerequisites = [self.get_lesson_from_id(
            p) for p in lesson.prerequisites]
        for prerequisite in prerequisites:
            # If the prerequisite is a source lesson, we stop the recursion
            if prerequisite == source_lesson:
                return [], level
            recursive, level_below = self.get_recursive_prerequisites(
                prerequisite, level=level + 1, source_lesson=source_lesson)
            # if the level below is lower than the current level, we need to invert the order
            if level_below < level:
                recursive = recursive[::-1]
            recursive_prerequisites += recursive
            # Append the current prerequisite to the end of the list
            recursive_prerequisites.append(prerequisite)

        # If we are in the first level, that means we are not in a recursive call
        # so we don't need the level variable anymore
        if level == 0:
            return recursive_prerequisites
        else:
            return recursive_prerequisites, level

verbose = False


def vprint(*t):
    if verbose:
        print(*t)


def unique_list_keep_last(seq):
    seq.reverse()
    seen = set()
    seen_add = seen.add
    seq = [x for x in seq if not (x in seen or seen_add(x))]
    seq.reverse()
    return seq


class ContentBaseClass:
    def __init__(self, path, _type):
        self.path = path
        # print(f'Initialising {_type} from path {self.path}')
        self.name = path.split('/')[-1]
        self._type = _type
        self._get_meta()

    def _get_meta(self):
        with open(os.path.join(self.path, f'{self._type}.yaml')) as f:
            meta = yaml.safe_load(f)
        self.id = meta.get('id', None)
        self.description = meta.get('description', '')
        self.prerequisites = meta.get('prerequisites', [])
        self.video = meta.get('video_url', None)

    # def _get_payload(self):
    #     """Method can be overwritten to provide a custom payload to the protected _create_or_update method"""
    #     return {
    #         'name': self.name,
    #         **self.meta,
    #         'role': []
    #     }

    def create_or_update(self):
        payload = self._get_payload()
        try:
            self.validate()
        except Exception as e:
            print('\t\t\tValidation failed. Create/update aborted')
            print(f'\t\t\tThe error was: {e}')
            print('\t\t\tThe final payload was:', payload)
            return
        api.create_or_update(self._type, payload)

    def __repr__(self):
        return self.name
    
    def __str__(self) -> str:
        return self.name

    def validate(self):
        try: 
            is_valid_uuid(self.id)
        except ValueError:
            raise ValueError(f'{self._type} {self.name} has an invalid ID, make sure it is a valid UUID')
        except AttributeError:
            raise AttributeError(f'{self._type} {self.name} does not have an ID')

        dev_assert(self.description, f'{self._type} {self.name} does not have a description')
        if self._type == 'lesson':
            assert self.notebook or self.video, f"{self.path} is missing a notebook or video, make sure there is a Notebook.ipynb or a video folder with a video.yaml file in it"


class MultipleContentBaseClass:
    def __init__(self, path, ContentClass):
        self.path = path
        self.ContentClass = ContentClass

    def _get_contents(self):
        content = os.listdir(self.path)
        content = [c for c in content if c[0] != '.']
        content = [os.path.join(self.path, m) for m in content]
        content = [fp for fp in content if os.path.isdir(fp)]
        return [self.ContentClass(m) for m in content]


class IndexedContentBaseClass(ContentBaseClass):
    def __init__(self, *args):
        super().__init__(*args)
        self.__set_index()

    def __set_index(self):
        try:
            # will fail if split does not result in 2 items
            idx, name = self.name.split(". ")
        except:
            raise NameError(
                f"{self.name} was expected to be numbered and contain '. ', but didn't"
            )
        self.idx = int(idx)
        self.name = name

    def _get_payload(self):
        return {
            'idx': self.idx,
            **super()._get_payload()
        }


class Unit(ContentBaseClass):
    def __init__(self, path):
        super().__init__(path, 'unit')
        self.modules = Modules(self.path)

    def _get_payload(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "modules": self.modules._get_payload()
        }


class Units(MultipleContentBaseClass):
    def __init__(self, path: str = 'Content/units'):
        super().__init__(path, Unit)
        self.units = self._get_contents()

    def __iter__(self):
        for unit in self.units:
            yield unit


class Module(IndexedContentBaseClass):
    def __init__(self, path):
        super().__init__(path, 'module')
        self.lessons = Lessons(self.path)
        # The structure of the modules have a list of dictionaries 
        # as opposed to a list of strings
        if self.prerequisites:
            self.prerequisites = [p['id']
                                  for p in self.prerequisites]
        self._set_parent_unit_id()

    def _get_payload(self):
        return {
            "id": self.id,
            "name": self.name,
            "unit_id": self.unit_id,
            "description": self.description,
            "idx": self.idx,
            "lessons": self.lessons._get_payload()
        }

    def _set_parent_unit_id(self):
        unit_meta_path = os.path.join(
            *self.path.split("/")[:-1], "unit.yaml")
        with open(unit_meta_path) as f:
            unit_meta = yaml.safe_load(f)
        self.unit_id = unit_meta["id"]


class Modules(MultipleContentBaseClass):
    def __init__(self, path):
        super().__init__(path, Module)
        self.modules = self._get_contents()

    def __iter__(self):
        for module in self.modules:
            yield module

    def _get_payload(self):
        module_payload = []
        for module in self.modules:
            module_payload.append(module._get_payload())

        return module_payload


class Lesson(IndexedContentBaseClass):
    def __init__(self, path):
        super().__init__(path, 'lesson')
        self._set_parent_module_id()
        self._set_notebook()
        self._set_video_url()
        self._set_recorded()
        self._set_needs_uploading()
        self._set_practicals()
        self._set_cover_image()

    def _set_parent_module_id(self):
        module_meta_path = os.path.join(
            *self.path.split("/")[:-1], "module.yaml")
        with open(module_meta_path) as f:
            module_meta = yaml.safe_load(f)
        self.module_id = module_meta["id"]
        self.module_idx = int(self.path.split("/")[-2].split(". ")[0])

    def _set_notebook(self):
        notebook_path = os.path.join(self.path, "Notebook.ipynb")
        if os.path.exists(notebook_path):
            self.notebook = Notebook(notebook_path)
        else:
            self.notebook = None

    def _set_video_url(self):
        # Add video_url if it exists
        if not self.video:

            try:
                with open(os.path.join(self.path, "video/video.yaml")) as f:
                    video_meta = yaml.safe_load(f)
                self.video = video_meta["video_url"]
            except FileNotFoundError:
                self.video = None

    def _set_recorded(self):
        raw_video_path = os.path.join(self.path, "video", "raw")
        if os.path.exists(raw_video_path) and (len(os.listdir(raw_video_path)) > 0):
            self.recorded = True
        else:
            self.recorded = False

    def _set_needs_uploading(self):

        video_exists = glob(os.path.join(self.path, "video", "video.m*")
                            ) or glob(os.path.join(self.path, "video", ".video.*"))
        self.needs_uploading = (not self.video) and video_exists

    def _set_practicals(self):
        self.practicals = Practicals(self.path)

    def _set_cover_image(self):
        '''
        Sets the image URL that will be used in the portal for the lesson
        '''
        # Check that there is a file called cover_img regardless of extension
        cover_img_path = glob(os.path.join(self.path, "cover_image.*"))
        if cover_img_path:
            # Check that the file is an image
            if cover_img_path[0].endswith((".png", ".jpg", ".jpeg")):
                s3_path = f"https://s3-eu-west-1.amazonaws.com/{S3_PUBLIC_BUCKET}/cover-images/Lessons/{self.id}.png"
                self.cover_img = s3_path
                self.cover_img_path = cover_img_path[0]
            else:
                raise ValueError(
                    f"Cover image for lesson {self.id} must be a png, jpg, or jpeg")
        else:
            self.cover_img = None
            self.cover_img_path = None

    def _get_payload(self):
        return {
            "id": self.id,
            "name": self.name,
            "module_id": self.module_id,
            "notebook_url": self.notebook.url if self.notebook else None,
            "description": self.description,
            "video_url": self.video,
            "idx": self.idx,
            "practicals": self.practicals._get_payload(),
            "cover_img": self.cover_img,
        }

    def validate(self):
        try:
            super().validate()
            self.practicals.validate()
            if self.notebook: self.notebook.validate()
            common_extraneous_files = [
                ".lesson.yaml",
                ".practicals.yaml",
                "practical.yaml",
                # ".challenges.yaml" # TODO migrate all old ones over
            ]
            for filename in common_extraneous_files:
                assert not os.path.exists(os.path.join(
                    self.path, filename)), f'Lesson folder should not contain a file named "{filename}"'
            # TODO remove all extraneous files rather than just common ones
            
        except AssertionError as e:
            raise AssertionError(f"{e}\n{self.path}")


class Lessons(MultipleContentBaseClass):
    def __init__(self, path):
        super().__init__(path, Lesson)
        self.lessons = self._get_contents()

    # def __iter__(self):
    #     return self.lessons

    def __iter__(self):
        for lesson in self.lessons:
            yield lesson

    def _get_payload(self):
        lesson_payload = []
        for lesson in self.lessons:
            lesson_payload.append(lesson._get_payload())

        return lesson_payload

class Notebook:
    def __init__(self, path):
        self.path = path
        self.cells = nbformat.read(path, as_version=4)['cells']
        self.name = path.split('/')[-2]
        self.url = self._set_notebook_url(path)

    def validate(self):
        '''
        Loads each Notebook.ipynb found in lessons and check they're valid JSON. 
        '''
        cells = nbformat.read(self.path, as_version=4)['cells']
        dev_assert(cells[0]['cell_type'] == 'markdown', f"The first cell in notebook {self.name} is not a markdown cell")
        dev_assert(cells[0]['source'].startswith("# "), f"The first cell in notebook {self.name} is not a title (it doesn't start with #)")
        # Extract and check the title
        first_line = cells[0]['source'].split("\n")[0]
        first_title = first_line.split("#")[-1].strip()
        self._check_title(first_title)
        headings = self._get_headings(cells)
        dev_assert("## Introduction" in headings, f'In the "{self.name}" notebook there is no heading for introduction. Add a markdown cell with "## Introduction"')
        dev_assert("## Key Takeaways" in headings, f'In the "{self.name}" notebook there is no heading for the outro. Add a markdown cell with ## Key Takeaways')
        dev_assert("Assessment" not in headings, f'In the "{self.name}" notebook there is a heading for the assessments. Remove those assessment, and move them to the practical')
        dev_assert("Non-Assessment" not in headings, f'In the "{self.name}" notebook there is a heading for non-assessments. Remove those assessment, and move them to the practical')
    
    @staticmethod
    def _set_notebook_url(path):
        content_repo = os.environ.get("PUBLIC_CONTENT_REPO")
        colab_link = f"https://colab.research.google.com/github/{content_repo}/blob/main/{path}"
        colab_link = urllib.parse.quote(colab_link, safe="%/:")
        return colab_link
    
    def _check_title(self, text):
        # Checks that it doesn't start with number
        aux_text = dev_assert(not text[0].isdigit(),
                              f'The title of notebook "{self.name}" should\'t start with a number --> {text}',
                              additional=' '.join(text.split()[1:]))
        if aux_text:
            text = aux_text
        
        for idx, word in enumerate(text.split()):
            if word.lower() in words_to_not_capitalise and idx > 0:
                if word in string.punctuation:
                    continue
                dev_assert(word[0].islower(), f'In the title of notebook {self.name}, the word "{word}" should not be capitalised ({text})')
            else:
                dev_assert(word[0].isupper(), f'In the title of notebook {self.name}, the word "{word}" should be capitalised ({text})')

    @staticmethod
    def _get_headings(cells):
        headings = []
        for cell in cells:
            text = cell['source']
            text_lines = text.split('\n')
            titles = [title for title in text_lines if title.startswith("#")]
            headings.extend(titles)
        return headings


class Projects:
    def __init__(self, root_project_dir: str = "Projects/scenarios/"):
        self.root_project_dir = root_project_dir
        # TODO remove old projects causing issues
        skip_projects = [
            # "AirBnb-Multimodal-DL",
            # "Computer-Vision",
            # "Data-Collection-Pipeline",
            # "Deploying-an-Image-Segmentation-System",
            # "Facebook-Marketplace",
            # "Football-Match-Outcome-Prediction-System",
            # "Hangman",
            # "Pinterest-Data-Processing-Pipeline",
            # "Modelling-Airbnb-Property-Listings",
            # "Data-Analytics-Migration-Tableau",

            "Specialisation-Choice-MVP",
            "Hiring-Process"
        ]
        content = Content()
        lessons = content.lessons
        self.lesson_ids = [lesson.id for lesson in lessons]
        project_dirs = os.listdir(self.root_project_dir)
        project_dirs = [p for p in project_dirs if p not in skip_projects]
        self.projects = [Project(os.path.join(
            self.root_project_dir, project_dir)) for project_dir in project_dirs]

    def __iter__(self):
        for project in self.projects:
            yield project

    def validate(self):
        for project in self.projects:
            project.validate()
        self.validate_ids_unique_across_all_projects()
        self._validate_prereqs_are_in_lessons()
        
    def validate_ids_unique_across_all_projects(self):
        print('Validating ids unique across projects')
        ids = []
        for project in self.projects:
            ids.extend(project.get_ids())
        validate_ids_are_unique(ids)
        print('All project ids are unique')

    def _validate_prereqs_are_in_lessons(self):
        print('Validating prereqs are in lessons')
        for project in self.projects:
            for prereq in project.prerequisites:
                assert prereq in self.lesson_ids, f'Prerequisite {prereq} for project {project.name} is not in lessons'
        print('All project prereqs are in lessons')


class Project:
    def __init__(self, project_dir):
        project_fp = os.path.join(project_dir, "specification.yaml")
        with open(project_fp) as f:
            self.project = yaml.safe_load(f)
        project_name = project_fp.split('/')[-2]
        self.name = project_name
        self.path = project_fp
        # TODO validate proper case for name
        self.description = self.project["description"]
        self.milestones = self.project["milestones"]
        self.id = self.project["id"]
        self.tasks = []
        for milestone_idx, milestone in enumerate(self.milestones):
            self.tasks.extend([
                Task({
                    **t,
                    "milestone_idx": milestone_idx,
                    "idx": task_idx
                }) for task_idx, t in
                enumerate(milestone["tasks"])
            ])
        self._set_prerequisites()

    def _set_prerequisites(self):
        self.prerequisites = []
        # print(projects)
        # TODO create milestone client
        for milestone in self.milestones:
            # TODO use task client
            for task in self.tasks:
                self.prerequisites.extend(task.prerequisites)

    def validate(self):
        is_valid_uuid(self.id)
        self._validate_all_ids_valid()
        self._validate_all_ids_unique()
        for task in self.tasks:
            task.validate()

    def get_ids(self):
        return [
            self.project["id"],
            * [m["id"] for m in self.milestones],
            *[t.id for t in self.tasks]
        ]

    def _validate_all_ids_valid(self):
        for id in self.get_ids():
            is_valid_uuid(id)

    def _validate_all_ids_unique(self):
        ids = self.get_ids()
        validate_ids_are_unique(ids)


def validate_ids_are_unique(ids):
    duplicate_ids = get_duplicates(ids)
    try:
        assert len(duplicate_ids) == 0
    except AssertionError:
        raise ValueError(f"Duplicate IDs detected", duplicate_ids)


def get_duplicates(items):
    return [i for i, count in collections.Counter(
        items).items() if count > 1]


class Task:
    def __init__(self, task) -> None:
        # print(task)
        self.id = task["id"]
        self.description = task["description"]
        self.duration = task["duration"]
        self.idx = task["idx"]
        self.milestone_idx = task["milestone_idx"]
        if "prerequisites" not in task:
            self.prerequisites = []
        else:
            self.prerequisites = task['prerequisites']
            if self.prerequisites == None:
                raise TypeError('Prerequisites key defined as empty')
        # self._set_recursive_prerequisites()

    def set_recursive_prerequisites(self, content_client):
        # TODO remove content client from being passed in

        self.recursive_prerequisites = content_client.get_recursive_prerequisites(
            self.prerequisites)

    def validate(self):
        lowercase_description = self.description.lower()
        assert "In this task" not in lowercase_description, 'No task should say "In this task"'
        assert "In this milestone" not in lowercase_description, 'No task should say "In this milestone"'
        assert "Congratulations on finishing your project!" not in lowercase_description
        # assert " we " not in lowercase_description, 'Tasks should refer to the user with "you" instead of "we"' # not valid in a few cases
        # assert " our " not in lowercase_description, 'Tasks should refer to the user with "your" instead of "our"' # not valid in a few cases


class Practicals:
    def __init__(
        self,
        lesson_path: str,
    ):
        self.practicals = []
        self.lesson_path = lesson_path
        folder_path = os.path.join(lesson_path, "Practicals")
        if os.path.exists(folder_path):
            # Get all the folders in the practicals folder
            self.inner_folders = [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if os.path.isdir(os.path.join(folder_path, f))
            ]
            # Sort the folders by name so the idx attribute is consistent
            self.inner_folders.sort()
            # Check that there is a specification.yaml in each folder
            practicals: List[dict] = []
            for idx, folder in enumerate(self.inner_folders):
                specs = os.path.join(folder, "specifications.yaml")
                if not os.path.exists(specs):
                    print(f"WARNING: No specifications.yaml found in {folder}")
                    continue
                with open(os.path.join(folder, "specifications.yaml")) as f:
                    specification: dict = yaml.safe_load(f)
                assert isinstance(specification, dict), \
                    f'specification.yaml in {folder} should be a dictionary, not a {type(specification)}'
                practicals.append(
                    Practical(
                        specification,
                        idx=idx,
                        lesson_path=lesson_path,
                        notebook_folder_path=folder,
                    )
                )
            self.practicals.extend(practicals)

        self.practical_specs_path = os.path.join(
            lesson_path,
            "practicals.yaml"
        )
        if os.path.exists(self.practical_specs_path):
            with open(self.practical_specs_path) as f:
                specs: List[dict] = yaml.safe_load(f)
            practicals = [
                Practical(
                    practical,
                    idx,
                    lesson_path,
                )
                for idx, practical in enumerate(specs, start=len(self.practicals))
            ]
            self.practicals.extend(practicals)

    def __getitem__(self, idx):
        return self.practicals[idx]

    def _get_payload(self):
        practicals_payload = []
        for practical in self.practicals:
            practicals_payload.append(practical._get_payload())

        return practicals_payload

    def validate(self):
        for practical in self.practicals:
            practical.validate()


class Practical(ContentBaseClass):
    def __init__(
        self,
        practical: dict,
        idx: int,
        lesson_path: str,
        notebook_folder_path: str = None,
    ) -> None:
        '''
        Class for a practical

        Parameters
        ----------
        practical : dict
            The practical specification
        idx : int
            The index of the practical
        '''
        self.specs = practical
        self.notebook_folder_path = notebook_folder_path
        if self.notebook_folder_path:
            self.name = self.notebook_folder_path.split("/")[-1]
            # If there is a number at the start of the folder name, remove it
            if self.name[0].isdigit():
                try:
                    self.name = [i for i in self.name if not i.isdigit()]
                    self.name = "".join(self.name)
                    if self.name[0] == ".":
                        self.name = self.name[1:].strip()
                except IndexError:
                    print(f"WARNING: Could not parse name of practical {self.name}")
                    self.name = self.notebook_folder_path.split("/")[-1]
                except Exception as e:
                    print(f"WARNING: Could not parse name of practical {self.name}")
                    print(e)
                    self.name = self.notebook_folder_path.split("/")[-1]

            self.practical_notebook_path = self._set_practical_notebook()
            self.practical_notebook_url = self._set_practical_notebook_url()
        else:
            self.name: str = practical["name"]
            self.practical_notebook_path = None
            self.practical_notebook_url = None
        self.description: str = practical["description"]
        self.id: str = practical["id"]
        self.idx = idx
        self._type = "lesson/practicals"
        self.lesson_path = lesson_path
        self._set_lesson_id()
        self._set_practical_instructions()

    def _get_payload(self):
        return {
            "name": self.name,
            "description": self.description,
            "lesson_id": self.lesson_id,
            "id": self.id,
            "idx": self.idx,
            "notebook_url": self.practical_notebook_url,
        }

    def _set_lesson_id(self):
        lesson_meta_path = os.path.join(
            self.lesson_path,
            "lesson.yaml"
        )
        with open(lesson_meta_path) as f:
            lesson_meta = yaml.safe_load(f)
        self.lesson_id = lesson_meta["id"]

    def _set_practical_notebook(self):
        '''
        Checks if there is a Practical folder in that lesson
        and if there is, checks that inside it, there is a folder with
        the same name as the practical

        If there is, it will check the notebook path and set it
        as an attribute
        '''
        practical_notebook_path = os.path.join(
            self.notebook_folder_path,
            "Practical.ipynb"
        )
        if not os.path.exists(practical_notebook_path):
            return None
        else:
            return practical_notebook_path

    def _set_practical_notebook_url(
        self
    ) -> Optional[str]:
        '''
        Sets the practical notebook url as an attribute
        '''
        if self.practical_notebook_path is None:
            return None
        else:
            content_repo = os.environ.get("PUBLIC_PRACTICAL_REPO")
            colab_link = (f"https://colab.research.google.com/github/{content_repo}" +
                          f"/blob/main/{self.practical_notebook_path}")
            colab_link = urllib.parse.quote(colab_link, safe="%/:")
            return colab_link

    def _set_practical_instructions(self):
        '''
        Sets the necessary instructions for the practical
        '''
        self.instructions = {}
        possible_instructions = [
            "create",
            "read",
            "update",
            "delete",
            "upload",
            "run"
        ]
        if instructions := self.specs.get("instructions"):
            for instruction in instructions:
                if instruction not in possible_instructions:
                    warnings.warn(f"Instruction {instruction} is not a valid instruction"\
                                  f" for practical {self.name} in lesson {self.lesson_id}")
                else:
                    self.instructions[instruction] = True

    def validate(self):
        # print('validating practical', self.id)
        try:
            if self.notebook_folder_path:
                assert self.name, f"The practical in {self.notebook_folder_path} has no name"
                # If the notebook exists, check that the notebook is valid
                if self.practical_notebook_path:
                    try:
                        nb = nbformat.read(self.practical_notebook_path, as_version=4)
                        # Check that the first cell is a markdown cell with a heading
                        assert nb.cells[0].cell_type == "markdown", \
                            f"The first cell in the notebook {self.practical_notebook_path} should be a markdown cell"
                        assert nb.cells[0].source.startswith("#"), \
                            f"The first cell in the notebook {self.practical_notebook_path} should be a markdown cell with a heading"
                    except Exception as e:
                        raise AssertionError(f"Error reading notebook {self.practical_notebook_path}: {e}")

            else:
                assert self.name, f"The practical in {self.lesson_path} has no name"

            assert not self.name[0].isdigit() and self.name[1] != '.', \
                f'Practicals should not be numbered (name "{self.name}"'
            for idx, word in enumerate(self.name.split()):
                if word[0].isdigit():
                    continue
                if not word[0].isalpha():
                    continue
                if word.lower() in words_to_not_capitalise and idx > 0:
                    assert word[0].islower(
                    ), f'In practical names, the word "{word}" should not be capitalised'
                else:
                    assert word[0].isupper(
                    ), f'In practical names, the word "{word}" should be capitalised'

        except AssertionError as e:
            raise AssertionError(f"{e}\nPractical ID: {self.id}")


class Pathways:
    def __init__(self,
                 path: str = 'Pathways'):
        pathways_names = os.listdir(path)
        content = Content()
        lesson_ids = [lesson.id for lesson in content.lessons]
        self.pathways = [os.path.join(path, pathway) for pathway in pathways_names
                         if os.path.isdir(os.path.join(path, pathway))]
        self.pathways = [Pathway(pathway_dir=pathway,
                                 content_lesson_ids=lesson_ids)
                         for pathway in self.pathways]

    def __getitem__(self, idx):
        return self.pathways[idx]

    def __iter__(self):
        return iter(self.pathways)

    def validate(self):
        for pathway in self.pathways:
            print('validating pathway', pathway.name)
            pathway.validate()
        self._validate_unique_ids()

    def _validate_unique_ids(self):
        ids = [pathway.id for pathway in self.pathways]
        repeated_id_names = [pathway.name for pathway in self.pathways if ids.count(pathway.id) > 1]
        assert len(ids) == len(set(ids)), "Pathway IDs should be unique. The following pathways have repeated IDs: " + ", ".join(repeated_id_names)


class Pathway:
    def __init__(
        self,
        content_lesson_ids: list,
        pathway_dir: str,
    ) -> None:
        pathway_fp = os.path.join(pathway_dir, "pathway.yaml")
        self.name = pathway_dir.split("/")[-1]
        with open(pathway_fp) as f:
            self.specs = yaml.safe_load(f)
        if ("target_lessons" in self.specs) and (self.specs["target_lessons"] is not None):
            self.target_lesson = [lesson['name'] for lesson in self.specs["target_lessons"]]
        else:
            self.target_lesson = []
        if ("source_lessons" in self.specs) and (self.specs["source_lessons"] is not None):
            self.source_lesson = [lesson['name'] for lesson in self.specs["source_lessons"]]
        else:
            self.source_lesson = []
        if ("stop_prerequisites_from" in self.specs) and (self.specs["stop_prerequisites_from"] is not None):
            self.stop_prerequisites_from = [lesson['name'] for lesson in self.specs["stop_prerequisites_from"]]
        else:
            self.stop_prerequisites_from = []

        self.description = self.specs["description"]
        self.id = self.specs["id"]
        self.path = pathway_fp
        self.content_lesson_ids = content_lesson_ids
        self.lessons = self.specs["lessons"]
        self.lesson_ids = [lesson["id"] for lesson in self.lessons]
        self.lesson_names = [lesson['name'] for lesson in self.lessons]
        self._set_cover_image()
        self.payload = self._get_payload()

    def _get_payload(self):
        return {
            "name": self.name,
            "description": self.description,
            "id": self.id,
            "lessons": self.lesson_ids,
            "cover_img": self.cover_img
        }

    def _set_cover_image(self):
        '''
        Sets the image URL that will be used in the portal for the lesson
        '''
        # Check that there is a file called cover_img regardless of extension
        pathway_dir = self.path.split("pathway.yaml")[0]
        cover_img_path = glob(os.path.join(pathway_dir, "cover_image.*"))
        if cover_img_path:
            # Check that the file is an image
            if cover_img_path[0].endswith((".png", ".jpg", ".jpeg")):
                s3_path = f"https://s3-eu-west-1.amazonaws.com/{S3_PUBLIC_BUCKET}/cover-images/Pathways/{self.id}.png"
                self.cover_img = s3_path
                self.cover_img_path = cover_img_path[0]
            else:
                raise ValueError(
                    f"Cover image for lesson {self.id} must be a png, jpg, or jpeg")
        else:
            self.cover_img = None
            self.cover_img_path = None

    def validate(self):
        assert uuid.UUID(self.id, version=4), "Pathway ID is not a valid UUID"
        assert "description" in self.specs, "Pathway description is missing"
        assert self.specs['description'] != "", "Pathway description is empty"
        assert "lessons" in self.specs, "Pathway lessons are missing"

        for lesson in self.lessons:
            lesson_id = lesson["id"]
            assert uuid.UUID(lesson_id, version=4), "Lesson ID is not a valid UUID"
            assert lesson_id in self.content_lesson_ids, f"Lesson ID {lesson} is not in the lessons list"


if __name__ == "__main__":
    content = Content()
