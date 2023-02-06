import yaml
from utils.client import Content, Projects
import os


class Tree:
    def __init__(self, verbose=False) -> None:
        self.content = Content()
        self.verbose = verbose

    def create_recursive_prerequisites(self):
        projects = Projects()
        for project in projects:

            task_to_recursive_prereqs = {}

            for task in project.tasks:
                prerequisites_for_this_task = [self.content.get_lesson_from_id(
                    p) for p in task.prerequisites]
                recursive_tasks = []
                for prerequisite in prerequisites_for_this_task:
                    if self.verbose:
                        message = f"Creating prerequisites for {prerequisite.name}"
                        print(f"{message:*^100}")
                    recursive_tasks.extend(
                        self.content.get_recursive_prerequisites(prerequisite))
                    # We need to add the prerequisite itself to the list of recursive tasks
                    recursive_tasks.append(prerequisite)

                    if self.verbose: print(recursive_tasks)

                recursive_tasks = self.__keep_only_first(recursive_tasks)

                if self.verbose: print(f"\nPrerequisite for task {task.id}: {recursive_tasks}\n")

                recursive_prereqs_for_this_task = [
                    l.id for l in recursive_tasks]
                task_to_recursive_prereqs[task.id] = recursive_prereqs_for_this_task

            prereqs_file = os.path.join(
                *project.path.split('/')[:-1], "task-to-recursive-prereqs.yaml")
            with open(prereqs_file, 'w') as f:
                yaml.dump(task_to_recursive_prereqs, f)

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

    tree = Tree()
    tree.save_project_task_recursive_prerequisites()
