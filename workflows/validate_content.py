from utils.client import Content 

if __name__ == "__main__":

    content = Content()
    content.validate()
    lesson_ids = [lesson.id for lesson in content.lessons]
    for lesson in content.lessons:
        prereqs = lesson.prerequisites
        for prereq in prereqs:
            assert prereq in lesson_ids, f"Prerequisite {prereq} for lesson {lesson.name} does not exist"
