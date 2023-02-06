from .verify import get_errors_fails, mark_incomplete, mark_complete
import os
task1_id = 'bcf3c4f1-1547-4727-8e25-a14165eac6d6' # Download the model
task2_id = 'e82a250f-536f-4649-b3e2-2e8680a9119d' # Begin documenting your experience


task_name_list = [
        ('test_model_presence', task1_id),
        ('test_presence_readme', task2_id)
        ]


if 'milestone_2.txt' in os.listdir('.'):
    errors = get_errors_fails('milestone_2.txt')
    if len(errors) == 0:
        for task in task_name_list:
            mark_complete(task[1])
    else:
        for task_name, task_id in task_name_list:
            if task_name not in errors:
                mark_complete(task_id)
            else:
                mark_incomplete(task_id, errors[task_name])
                break