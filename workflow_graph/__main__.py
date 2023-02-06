# %%
import yaml
import os
from PIL import Image
from utils.client import Content, Projects
import networkx as nx
# Here since image is too large thinks it's a decompression DOS attack
Image.MAX_IMAGE_PIXELS = 933120000


def get_name(id: str, modules: list) -> str:
    for module in modules:
        if module["id"] == id:
            return module["name"]
    return "unknown"

class ContentGraph:

    def __init__(self, verbose: bool = False):
        self.content = Content()
        self.verbose = verbose

    def generate_full_content_graph(self,
                                    show: bool = True,
                                    save_path: str = "workflow_graph/images/graph.png"):
        g = self.get_graph_from_lesson_subset(self.content.lessons)
        self.plot_graph(g, show=show, save_path=save_path)

    def get_graph_from_lesson_subset(self,
                                     lessons,
                                     color_mode="default") -> nx.DiGraph:
        graph = nx.DiGraph()
        for lesson in lessons:
            # see other attrs here https://graphviz.gitlab.io/doc/info/attrs.html
            attrs = {
                "fillcolor": self._get_node_color(
                    lesson, mode=color_mode),
                "id": lesson.id
            }
            graph.add_node(lesson.name, **attrs)

            if self.verbose and len(lesson.prerequisites) == 0:
                print(f"{lesson.path} has no prerequisites")
            for prerequisite in lesson.prerequisites:
                try:
                    prerequisite = self.content.get_lesson_from_id(
                        prerequisite)
                except Exception as e:
                    print('Error with', prerequisite.name, 'in', lesson.path)
                    raise Exception(e)
                # We have to explicitely tell the name of the prerequisite
                # Otherwise it won't add the apostrophes to the string
                # and the existing lesson name wont be found
                graph.add_edge(prerequisite.name, lesson.name)
        return graph

    def _get_node_color(self, lesson, mode="default"):

        green = "#71D271"
        purple = '#BE2ED6'
        blue = '#3C68DB'
        amber = '#FBBB63'
        red = '#E05151'

        if mode == "default":
            if lesson.video:
                return green
            # elif lesson.recorded and lesson.notebook:
            #     return '#F2672C'}  # dark orange
            elif lesson.needs_uploading:
                return purple
            elif lesson.recorded:
                return blue
            elif lesson.notebook:
                return amber
            else:
                return red
        elif mode == "practicals_exist":
            if lesson.practicals:
                return green
            else:
                return red

    @staticmethod
    def plot_graph(graph: nx.DiGraph,
                   show=True,
                   save_path=None):
        # Get the graph image in a path
        args = {"path": save_path,
                "show": show}
        nx.nx_agraph.view_pygraphviz(graph, **args)

    def generate_project_content_graphs(self):
        # TODO remove old projects causing issues

        projects = self.set_all_projects_graph_attr()
        for project in projects:
            self.show_and_save(
                project.graph, fp=f"workflow_graph/images/project-dependencies/{project.name}.png")
            print()
        # input("hit enter to continue")

    def set_all_projects_graph_attr(self, graph_mode="default"):
        projects = Projects()
        for project in projects:
            # TODO put in project client
            print(project.name)
            print(project.path)
            project_prereqs = []
            for task in project.tasks:
                prerequisites_for_this_task = [self.content.get_lesson_from_id(
                    p) for p in task.prerequisites]
                recursive_tasks = []
                for prerequisite in prerequisites_for_this_task:
                    message = f"Creating prerequisites for {prerequisite.name}"
                    # print(f"{message:*^100}")
                    recursive_tasks.extend(
                        self.content.get_recursive_prerequisites(prerequisite))
                    # We need to add the prerequisite itself to the list of recursive tasks
                    recursive_tasks.append(prerequisite)
                    # print(recursive_tasks)
                recursive_tasks = self.__keep_only_first(recursive_tasks)
                # task_graph = self.get_graph_from_lesson_subset(recursive_tasks)

                print(
                    f"\nPrerequisite for task {task.id}: {recursive_tasks}\n")
                project_prereqs.extend(recursive_tasks)
            project_prereqs = self.__keep_only_first(project_prereqs)
            graph = self.get_graph_from_lesson_subset(
                project_prereqs, color_mode=graph_mode)
            project.graph = graph
        return projects

    def save_all_project_task_recursive_prerequisites(self):
        projects = Projects()
        for project in projects:
            self.save_project_task_recursive_prerequisites(project)

    def save_project_task_recursive_prerequisites(self, project):
        print(project.name)
        print(project.path)

        task_to_recursive_prereqs = {}

        for task in project.tasks:
            prerequisites_for_this_task = [self.content.get_lesson_from_id(
                p) for p in task.prerequisites]
            recursive_tasks = []
            for prerequisite in prerequisites_for_this_task:
                print(f"Creating prerequisites for {prerequisite.name}")
                recursive_tasks.extend(
                    self.content.get_recursive_prerequisites(prerequisite))
                # We need to add the prerequisite itself to the list of recursive tasks
                recursive_tasks.append(prerequisite)
                # print(recursive_tasks)
            recursive_tasks = self.__keep_only_first(recursive_tasks)

            if recursive_tasks:
                task_graph = self.get_graph_from_lesson_subset(
                    recursive_tasks)
                task_graph_save_dir = os.path.join(
                    project.path.replace("/specification.yaml", ""), "status", "task-prereqs")
                if not os.path.exists(task_graph_save_dir):
                    os.makedirs(task_graph_save_dir, exist_ok=True)
                task_graph_save_path = os.path.join(
                    task_graph_save_dir,
                    f"M{task.milestone_idx}T{task.idx}.png"
                )
                self.show_and_save(
                    task_graph,
                    task_graph_save_path
                )

            # print(
            #     f"\nPrerequisite for task {task.id}: {recursive_tasks}\n")
            recursive_prereqs_for_this_task = [
                lesson.id for lesson in recursive_tasks]
            task_to_recursive_prereqs[task.id] = recursive_prereqs_for_this_task

        # print(task_to_recursive_prereqs)
        prereqs_file = os.path.join(
            *project.path.split('/')[:-1], "task-to-recursive-prereqs.yaml")
        with open(prereqs_file, 'w') as f:
            yaml.dump(task_to_recursive_prereqs, f)
        print()

    def generate_project_practicals_exist(self):
        projects = self.set_project_graph_attr(graph_mode="practicals_exist")
        for project in projects:
            self.show_and_save(
                project.graph, fp=f"Projects/scenarios/{project.name}/status/practicals.png")
            print()

    @staticmethod
    def __keep_only_first(prereq_list: list) -> list:
        '''
        Iterate through the list of prerequisites and keep only the first instance of each prerequisite.

        Parameters
        ----------
        prereq_list : list
            List of prerequisites

        Returns
        -------
        list
            List of prerequisites with only the first instance of each prerequisite
        '''
        already_seen = []
        for task in prereq_list:
            if task not in already_seen:
                already_seen.append(task)
        return already_seen


if __name__ == '__main__':

    content_graph = ContentGraph()
    content_graph.generate_full_content_graph(show=False,
                                              save_path="Pathways/whole_content.png")
