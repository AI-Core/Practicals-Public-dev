from utils.client import Pathways  # noqa: E402
from utils.pathway_generator import PathwayGenerator  # noqa: E402
import yaml

if __name__ == "__main__":
    pathways = Pathways()
    pathway_ids = [pathway.id for pathway in pathways]
    for pathway in pathways:
        print(f"Validating pathway {pathway.name}...")
        pathway.validate()
        # Check that the pathway generated with the current content is the same as the one in the yaml file
        current_pathway = PathwayGenerator(
            name=pathway.name,
            target_lesson=pathway.target_lesson,
            source_lesson=pathway.source_lesson,
            stop_prerequisites_from=pathway.stop_prerequisites_from,
            delete_intermediate_lessons=True
        )
        current_pathway_lessons = current_pathway.get_pathway()
        current_pathway_lessons_ids = [lesson['id'] for lesson in current_pathway_lessons]
        for lesson in current_pathway_lessons:
            assert lesson['id'] in pathway.lesson_ids, \
                f"In pathway {pathway.name}, lesson {lesson['name']} with ID {lesson['id']}" + \
                " should be added to the pathway yaml file. Rerun the pathway generator to update the yaml file"
        for lesson in pathway.lessons:
            assert lesson['id'] in current_pathway_lessons_ids, \
                f"In pathway {pathway.name}, lesson {lesson['name']} with ID {lesson['id']}" + \
                " should be deleted from the pathway yaml file. Rerun the pathway generator to update the yaml file"

    print("All pathways are valid\n")

    membership_key_path = "Pathways/membership_keys.yaml"
    with open(membership_key_path, 'r') as f:
        membership_keys = yaml.safe_load(f)

    # assert that each membership key has a unique name
    membership_key_names = [membership_key["name"] for membership_key in membership_keys]
    assert len(membership_key_names) == len(set(membership_key_names)), \
        "Membership keys must have unique names. Please update the membership key yaml file"

    # assert that the pathways included in the membership keys are valid
    for membership_key in membership_keys:
        print(f"Validating membership key {membership_key['name']}...")
        membership_pathways = membership_key["pathways"]
        membership_pathway_ids = [pathway["id"] for pathway in membership_pathways]
        for membership_pathway_id in membership_pathway_ids:
            assert membership_pathway_id in pathway_ids, \
                f"In membership key {membership_key['name']}, pathway {membership_pathway_id} does not exist. " + \
                "Please update the membership key yaml file"

    print("All membership keys are valid. Have a nice day! :)")

