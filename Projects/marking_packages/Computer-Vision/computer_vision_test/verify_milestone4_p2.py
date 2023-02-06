from .verify import get_errors_fails, mark_incomplete, mark_complete
import os

task1_id = '2ca4b14e-76dc-44a3-bfcd-052cf78615ef' # Store the user's and the computer's choices
task2_id = 'ae562b8c-bb0f-4861-a9d3-f8695953918b' # Figure out who won
task3_id = 'c1dfcdc5-97a4-4780-ab07-a0c4b785fcd2' # Create a function to simulate the game
task4_id = 'bd6076ef-ac2e-45a1-b38c-b5b1d733f63c' # Update your documentation

task_name_list = [
    ('test_get_computer_choice_user_choice', task1_id),
    ('test_get_winner', task2_id),
    ('test_play_game', task3_id),
    ('test_presence_readme', task4_id),
]

if 'milestone_4_p2.txt' in os.listdir('.'):
    errors = get_errors_fails('milestone_4_p2.txt')
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