from utils import client
import argparse
import openai
import os
from typing import List, Tuple
import yaml
import uuid

def get_lesson_path(lesson_name, module_name):
    content = client.Content()
    if lesson_name is None:
        lesson_name = input("Enter lesson name: ")

    # Get all the available lessons
    lessons = content.lessons

    # Gets all the lessons with the name provided by the user
    matching_lessons = [l for l in lessons if l.name == lesson_name]
    if len(matching_lessons) == 0:
        raise ValueError(f"No lesson with name {lesson_name}")
    # If there are more than one lesson with the same name, the user should provide the module name
    elif len(matching_lessons) > 1:
        print('Multiple lessons with this name:')
        for lesson in matching_lessons:
            print(lesson.path)
        if module_name == "All":
            print("Please provide the module name when calling this script")
            exit(1)
        else:
            for lesson in matching_lessons:
                if module_name in lesson.path:
                    matching_lesson = lesson
                    break
            else:
                raise ValueError(f"No lesson with name {lesson_name} in module {module_name}")
    else:
        matching_lesson = matching_lessons[0]

    print(f"Lesson path: {matching_lesson.path}")
    return matching_lesson.path


def generate_prompt(n_practicals: int,
                    lesson_name: str,
                    topic: str = None,
                    additional: str = None):
    '''
    Generates a prompt for the OpenAI API to generate practicals

    Parameters
    ----------
    n_practicals: int
        Number of practicals to generate
    lesson_name: str
        Name of the lesson to generate practicals for
    topic: str
        Topic of the practicals to generate. If None, it will not be included in the prompt
    '''
    prompt = f'''
        Given the following practicals:
        
        1. Print with Multiple Arguments: Assign your age to a variable, then, using a single print statement with multiple parameters, print "Age: " followed by your age.
        
        2. Sorting with Lambda Functions: Create a list with 5 tuples, where each tuple contains a name and a number. Then, using the `sort` function, create a lambda function for each of the following bullet points:
            - Sort the list by the number in each tuple
            - Sort the list by the name in each tuple
            - Sort the list by the length of the name in each tuple
            - Sort the list by the length of the name in each tuple, but in reverse order
        
        3. A bucket full of Cats:
            - Create an S3 bucket
            - Create an IAM user, and store your credentials    
            - If you haven't, install aws cli, and configure your local machine using aws configure    
            - Install boto3    
            - Download images from this website 'https://all-free-download.com/free-photos/cute-cat-jpg.html'    
            - Upload them to your S3 bucket using boto3
        
        4. Binary Generator Comprehension: Create an generator comprehension that infinitely generates ones or zeros randomly
        

        Generate {n_practicals} practicals in increasing difficulty for {lesson_name}
        '''

    if topic:
        prompt += f" in the topic of {topic}"

    if additional:
        prompt += f" {additional}"

    return prompt


def clean_practical(practicals: List[str]):
    '''
    Cleans the practicals by removing empty lines and lines that do not start with a number

    Parameters
    ----------
    practicals: List[str]
        List of practicals to clean

    Returns
    -------
    cleaned_practicals: List[str]
        List of cleaned practicals
    '''

    cleaned_practicals = [p.strip() for p in practicals if p.strip() != ""]
    cleaned_practicals = [p for p in cleaned_practicals if p[0].isdigit()]

    return cleaned_practicals


def verify_practicals(practicals: List[str]) -> List[dict]:
    '''
    Checks that the practicals are valid by observing if there is a colon
    The left hand side of the colon is the title of the practical and 
    the right hand side is the description

    It returns a list of dictionaries with the title and description of the practicals
    if all the practicals have a good structure. Otherwise, it will simply return None

    Parameters
    ----------
    practicals: List[str]
        List of practicals to verify and convert to a list of dictionaries
    '''
    valid_practicals = []
    for practical in practicals:
        if ":" not in practical:
            return None
        print(practical)
        title, description = practical.split(":", 1)
        # Remove the number from the title
        title = title.split(" ", 1)[1]
        # Removes trailing spaces from the description
        description = description.strip()
        valid_practicals.append({"name": title, "description": description})
    return valid_practicals
    


def generate_practicals(number_practicals: int,
                        lesson_name: str,
                        topic: str,
                        additional: str):
    prompt = generate_prompt(number_practicals, lesson_name, topic, additional)
    while True:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.5,
            max_tokens=3000,
            top_p=0.7,
            best_of=3,
            frequency_penalty=0.2,
            presence_penalty=0.25
        )
        practicals = response.choices[0].text.split("\n")
        cleaned_practicals = clean_practical(practicals)
        dict_practicals = verify_practicals(cleaned_practicals)
        if dict_practicals is not None:
            break
    return dict_practicals


def parse_arguments() -> Tuple[str, str, int, str, str]:
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--lesson", help="Name of the lesson to generate practicals for")
    parser.add_argument("-m", "--module", help="Name of the module corresponding to the lesson. If not provided, it will look inside all modules.", default="All")
    parser.add_argument("-n", "--number", help="Number of practicals to generate", default=5, type=int)
    parser.add_argument("-t", "--topic", help="Topic of the practicals to generate. Use it to give a hint to the GPT-3 model")
    parser.add_argument("--additional", help="Additional text to add to the prompt", default=None)
    args = parser.parse_args()
    lesson_name = args.lesson
    module_name = args.module
    number_practicals = args.number
    topic = args.topic
    additional = args.additional
    if topic == 'Any': topic = None
    if additional == 'Any': additional = None
    assert number_practicals > 0, "Number of practicals must be greater than 0"
    assert lesson_name is not None, "Lesson name must be provided"
    assert len(lesson_name) > 0, "Lesson name must be provided"

    return lesson_name, module_name, number_practicals, topic, additional


if __name__ == "__main__":
    openai.api_key = os.environ["OPENAI_TOKEN"]
    lesson_name, module_name, number_practicals, topic, additional = parse_arguments()
    lesson_path = get_lesson_path(lesson_name, module_name)
    practicals = generate_practicals(number_practicals, lesson_name, topic, additional)
    
    # Add the practicals to the lesson
    for practical in practicals:
        practical.update({"id": str(uuid.uuid4())})

    practical_path = os.path.join(lesson_path, "practicals.yaml")
    # Create or append to the practicals file
    if os.path.exists(practical_path):
        with open(practical_path, "r") as f:
            practicals_data = yaml.safe_load(f)
        practicals_data += practicals
    else:
        practicals_data = practicals

    with open(practical_path, "w") as f:
        yaml.dump(practicals_data, f)

