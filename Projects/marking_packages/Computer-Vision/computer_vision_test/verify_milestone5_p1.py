from .verify import get_errors_fails, mark_incomplete, mark_complete
import os

task1_id = '8dfaeb61-7a53-45e7-bd2f-f3939f172446'  # Putting all together
task2_id = 'c6c2c356-c83f-4a01-896f-739eec6a05bc'  # Count down
task3_id = '3891db35-2f65-43bd-849c-cde77ac0cb56'  # Repeat until a player gets three victories
task5_id = '90885a05-24f5-43a2-b4fe-962a2baaddb4'  # Update your documentation


if 'milestone_5_p1.txt' in os.listdir('.'):
    errors = get_errors_fails('milestone_5_p1.txt')
    print(errors)
    if len(errors) != 0:
        mark_incomplete(task1_id, errors['test_camera_rps_presence'])