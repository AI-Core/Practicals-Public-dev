from .verify import get_errors_fails, mark_incomplete, mark_complete
import os

task1_id = '8dfaeb61-7a53-45e7-bd2f-f3939f172446' # Putting all together
task2_id = 'c6c2c356-c83f-4a01-896f-739eec6a05bc' # Count down
task3_id = '3891db35-2f65-43bd-849c-cde77ac0cb56' # Repeat until a player gets three victories
task5_id = '90885a05-24f5-43a2-b4fe-962a2baaddb4' # Update your documentation

task_name_list = [
    ('test_prediction_presence', task1_id),
    ('test_time_presence', task2_id),
    ('test_number_wins', task3_id),
    ('test_presence_readme', task5_id),
]

if 'milestone_5_p2.txt' in os.listdir('.'):
    errors = get_errors_fails('milestone_5_p2.txt')
    print(errors)
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