from generate_practicals import generate_practicals, get_lesson_path
import openai
import os
import uuid
import yaml

def generate_multiple_practicals(number_practicals: int,
                                 lessons: list,
                                 topics: list,
                                 additional: list
                                    ) -> list:
    '''
    Generates multiple practicals by calling generate_practicals
    '''
    practicals = []
    for i in range(len(lessons)):
        practicals.append(generate_practicals(number_practicals, lessons[i], topics[i], additional[i]))
    return practicals

if __name__ == "__main__":
    openai.api_key = os.getenv("OPENAI_TOKEN")
    
    # YOUR INPUT HERE
    number_practicals = 5
    lessons = [
            'Numpy - Intro',
            'Numpy - Array Operations',
            'Numpy - Reshape and Broadcasting',
            # 'Putting a Local Git Repo on GitHub Correctly'
               ]
    topics = [
        'NumPy',
        'NumPy',
        'Numpy',
        # 'Git and GitHub'
        ]
    additional = [
        'Create practicals with different titles and capitalise the first letter of each word in the title',
        'Create practicals with different titles and capitalise the first letter of each word in the title',
        'Create practicals with different titles and capitalise the first letter of each word in the title',
        # 'Create practicals with different titles and capitalise the first letter of each word in the title',
        # 'Create practicals with different titles and capitalise the first letter of each word in the title',
        # 'Create easy practicals',
        # 'Create easy practicals'
        # None
        ]

    practicals = generate_multiple_practicals(number_practicals, lessons, topics, additional)
    for n, lesson_practicals in enumerate(practicals):
        for practical in lesson_practicals:
            practical.update({'id': str(uuid.uuid4())})
        print(lessons[n])
        lesson_path = get_lesson_path(lessons[n], 'All')
        practical_path = os.path.join(lesson_path, 'practicals.yaml')
        if os.path.exists(practical_path):
            with open(practical_path, "r") as f:
                practicals_data = yaml.safe_load(f)
            practicals_data += lesson_practicals
        else:
            practicals_data = lesson_practicals

        with open(practical_path, "w") as f:
            yaml.safe_dump(practicals_data, f, width=4096)



