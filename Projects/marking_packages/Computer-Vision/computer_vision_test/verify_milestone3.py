from .verify import get_errors_fails, mark_incomplete, mark_complete
import os

task1_id = '708b5625-63e0-4aaa-b941-97bb802f4954'  # Complete the installation of dependencies

# test_requirements_presence

if 'milestone_3.txt' in os.listdir('.'):
    errors = get_errors_fails('milestone_3.txt')
    if len(errors) != 0:
        mark_incomplete(task1_id, errors['test_requirements_presence'])
    else:
        mark_complete(task1_id)